"""GRU-D (Che et al. 2018, Sci Rep 8:6085) for (multivariate) series with missing values.

Inputs per step: x_t (D), m_t (D), delta_t (D: steps since last observation).
  x_hat = m*x + (1-m)*(g_x*x_last + (1-g_x)*x_mean),   g_x = exp(-relu(w_x*delta + b_x)) (diagonal)
  h     = g_h * h,                                     g_h = exp(-relu(W_h delta + b_h))
  h     = GRUCell([x_hat, m], h)
Classifier: linear layer on the final hidden state. Training: Adam (lr 1e-3), batch 64,
max 60 epochs, early stopping (patience 8) on a stratified 20% validation split drawn from the
training set only; the best-validation-loss weights are restored. x_mean is computed on training data.
"""
from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split


class GRUD(nn.Module):
    def __init__(self, d_in, hidden, n_classes, x_mean):
        super().__init__()
        self.register_buffer("x_mean", torch.as_tensor(x_mean, dtype=torch.float32))
        self.w_x = nn.Parameter(torch.zeros(d_in))
        self.b_x = nn.Parameter(torch.zeros(d_in))
        self.decay_h = nn.Linear(d_in, hidden)
        self.cell = nn.GRUCell(2 * d_in, hidden)
        self.out = nn.Linear(hidden, n_classes)
        self.hidden = hidden

    def forward(self, x, m, delta):  # (B, T, D)
        B, T, D = x.shape
        h = x.new_zeros(B, self.hidden)
        x_last = self.x_mean.expand(B, D).clone()
        for t in range(T):
            xt, mt, dt = x[:, t], m[:, t], delta[:, t]
            gx = torch.exp(-torch.relu(self.w_x * dt + self.b_x))
            gh = torch.exp(-torch.relu(self.decay_h(dt)))
            x_hat = mt * xt + (1 - mt) * (gx * x_last + (1 - gx) * self.x_mean)
            h = gh * h
            h = self.cell(torch.cat([x_hat, mt], dim=1), h)
            x_last = torch.where(mt > 0, xt, x_last)
        return self.out(h)


def _prep(X):
    """X: (n, D, T) with NaN -> x (n,T,D) zero-filled, m, delta (steps since last obs, capped)."""
    X = np.asarray(X, dtype=np.float32)
    if X.ndim == 2:
        X = X[:, None, :]
    X = np.transpose(X, (0, 2, 1))
    m = (~np.isnan(X)).astype(np.float32)
    x = np.nan_to_num(X, nan=0.0)
    n, T, D = x.shape
    delta = np.zeros_like(x)
    for t in range(1, T):
        delta[:, t] = np.where(m[:, t - 1] > 0, 1.0, delta[:, t - 1] + 1.0)
    return x, m, delta / max(T, 1)


def run_grud(Xtr, ytr, Xte, seed, hidden=64, epochs=60, patience=8, batch=64, lr=1e-3, threads=4):
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(threads)
    t0 = time.perf_counter()
    classes = np.unique(ytr)
    yi = np.searchsorted(classes, ytr)
    x, m, dl = _prep(Xtr)
    with np.errstate(invalid="ignore"):
        xm = np.nanmean(np.where(m > 0, x, np.nan).reshape(-1, x.shape[2]), axis=0)
    xm = np.nan_to_num(xm, nan=0.0)
    strat = yi if np.bincount(yi).min() >= 2 else None
    itr, iva = train_test_split(np.arange(len(yi)), test_size=0.2, random_state=seed, stratify=strat)
    T = lambda a: torch.from_numpy(a)
    model = GRUD(x.shape[2], hidden, len(classes), xm)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    lossf = nn.CrossEntropyLoss()
    best, best_state, bad = np.inf, None, 0
    rng = np.random.RandomState(seed)
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(itr)
        for s in range(0, len(perm), batch):
            b = perm[s:s + batch]
            opt.zero_grad()
            loss = lossf(model(T(x[b]), T(m[b]), T(dl[b])), T(yi[b]))
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
        model.eval()
        with torch.no_grad():
            vl = float(lossf(model(T(x[iva]), T(m[iva]), T(dl[iva])), T(yi[iva])))
        if vl < best - 1e-4:
            best, bad = vl, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    t1 = time.perf_counter()
    xe, me, de = _prep(Xte)
    model.eval()
    with torch.no_grad():
        s = torch.cat([model(T(xe[i:i + 512]), T(me[i:i + 512]), T(de[i:i + 512])) for i in range(0, len(xe), 512)]).numpy()
    t2 = time.perf_counter()
    return dict(pred=classes[s.argmax(1)], score=s, fit_s=t1 - t0, predict_s=t2 - t1,
                n_features=sum(p.numel() for p in model.parameters()), epochs=ep + 1)
