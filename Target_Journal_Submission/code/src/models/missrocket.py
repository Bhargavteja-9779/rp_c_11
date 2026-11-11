"""MissRocket: MiniRocket for series with missing values, using observed-tap-weighted pooling
whose strength is selected from the training data.

Pipeline for a series x with observation mask m:
  1. Gap filling: x~ = linear interpolation of the observed points (edges: nearest value).
  2. Responses: standard MiniRocket kernels on x~ (84 kernels, dilations, biases as in MiniRocket).
  3. Reliability of each response: c_t = number of truly observed taps among the 9 taps
     (out-of-bounds padding taps count as observed, as in MiniRocket).
  4. Weighted PPV pooling:  PPV_gamma = sum_t w_gamma(c_t) 1[C_t > b] / sum_t w_gamma(c_t),
     with w_gamma(c) = (c/9)**gamma. gamma = 0 recovers MiniRocket on the interpolated series.
  5. Optional missingness-pattern features: MiniRocket on the binary mask m.
  6. (gamma, mask on/off) are selected on the TRAINING set by the efficient leave-one-out
     (generalised cross-validation) criterion of the ridge head, the same criterion MiniRocket
     uses to choose the ridge penalty. No test information is used.

Because the weight depends only on the integer count c, PPV for all gammas is obtained
from per-count histograms of exceedances computed in a single pass.
"""
from __future__ import annotations

import numpy as np
from numba import njit, prange
from sklearn.linear_model import RidgeClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.models.maskrocket import (NUM_KERNELS, CONV_MODES, MaskRocket, _fit_biases, _fit_dilations,
                                   _quantiles, _responses, _taps)
from src.preprocessing.imputation import IMPUTERS, impute_linear

DEFAULT_GAMMAS = (0.0, 0.5, 1.0, 2.0)


@njit(parallel=True, cache=True)
def _transform_hist(X, M, dilations, nfpd, biases, wtab):
    """Return features (n, G, nfeat) for the G weight tables in wtab (G, 10)."""
    n, L = X.shape
    nfeat = biases.shape[0]
    G = wtab.shape[0]
    out = np.zeros((n, G, nfeat), dtype=np.float32)
    ones = np.ones(10, dtype=np.float32)
    for i in prange(n):
        C = np.zeros(L, dtype=np.float32)
        S = np.zeros(L, dtype=np.float32)
        V = np.zeros((9, L), dtype=np.float32)
        O = np.zeros((9, L), dtype=np.float32)
        cnt = np.zeros(L, dtype=np.int64)
        hist_num = np.zeros(10, dtype=np.float64)
        hist_den = np.zeros(10, dtype=np.float64)
        fs = 0
        for di in range(dilations.shape[0]):
            d = dilations[di]
            nf = nfpd[di]
            pad = ((9 - 1) * d) // 2
            p0 = di % 2
            _taps(X[i], M[i], d, 3, np.float32(1.0), V, O)
            for t in range(L):
                c = 0.0
                for j in range(9):
                    c += O[j, t]
                cnt[t] = np.int64(c)
            for k in range(NUM_KERNELS):
                _responses(V, O, k, 3, 0, ones, C, S)  # C on gap-filled values; S unused here
                p1 = (p0 + k) % 2
                t0 = 0
                t1 = L
                if p1 == 1 and L > 2 * pad:
                    t0 = pad
                    t1 = L - pad
                for c in range(10):
                    hist_den[c] = 0.0
                for t in range(t0, t1):
                    hist_den[cnt[t]] += 1.0
                for f in range(nf):
                    b = biases[fs + f]
                    for c in range(10):
                        hist_num[c] = 0.0
                    for t in range(t0, t1):
                        if C[t] > b:
                            hist_num[cnt[t]] += 1.0
                    for g in range(G):
                        num = 0.0
                        den = 0.0
                        for c in range(10):
                            num += wtab[g, c] * hist_num[c]
                            den += wtab[g, c] * hist_den[c]
                        out[i, g, fs + f] = num / den if den > 0 else 0.0
                fs += nf
    return out


def _wtab(gammas):
    c = np.arange(10, dtype=np.float64) / 9.0
    return np.stack([np.ones(10) if g == 0 else c ** g for g in gammas]).astype(np.float32)


def _ridge():
    return make_pipeline(StandardScaler(), RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)))


class MissRocket:
    """Classifier (transform + ridge head). Default: gamma = 1, no mask features (the proposed method).
    With fixed=None, (gamma, mask) is selected on the training set by ridge LOO (ablation 'MissRocket-select')."""

    def __init__(self, num_features=10_000, gammas=DEFAULT_GAMMAS, mask_options=(False, True),
                 mask_features=1000, random_state=None, fixed=(1.0, False), imputer="linear"):
        self.imputer = imputer
        self.num_features = num_features
        self.gammas = tuple(gammas)
        self.mask_options = tuple(mask_options)
        self.mask_features = mask_features
        self.random_state = random_state
        self.fixed = fixed  # (gamma, use_mask); default (1.0, False) = the proposed method. None -> select on train.

    def _prep(self, X):
        X = np.asarray(X, dtype=np.float32)
        M = (~np.isnan(X)).astype(np.float32)
        if self.imputer == "knn":  # cross-series kNN imputer fit on the training set only
            V = impute_linear(self.knn_.transform(X))
        else:
            V = IMPUTERS[self.imputer](X)
        return np.ascontiguousarray(V, dtype=np.float32), np.ascontiguousarray(M)

    def _features(self, x, m, gammas):
        return _transform_hist(x, m, self.dilations_, self.nfpd_, self.biases_, _wtab(gammas))

    def fit(self, X, y):
        rng = np.random.RandomState(self.random_state)
        if self.imputer == "knn":
            from src.preprocessing.imputation import KNNSeriesImputer
            self.knn_ = KNNSeriesImputer(5).fit(np.asarray(X, dtype=np.float32))
        x, m = self._prep(X)
        L = x.shape[1]
        self.dilations_, self.nfpd_ = _fit_dilations(L, self.num_features, 32)
        q = _quantiles(NUM_KERNELS * int(np.sum(self.nfpd_)))
        self.biases_ = _fit_biases(x, m, self.dilations_, self.nfpd_, q, CONV_MODES["imputed"], 0,
                                   _wtab([1.0])[0], np.float32(1.0), int(rng.randint(2**31 - 1)))
        need_mask = (self.fixed[1] if self.fixed else any(self.mask_options))
        if need_mask:
            self.mask_rocket_ = MaskRocket(num_features=self.mask_features, conv="zero_fill", pooling="all",
                                           random_state=int(rng.randint(2**31 - 1))).fit(m)
            Fm = self.mask_rocket_.transform(m)
        gammas = (self.fixed[0],) if self.fixed else self.gammas
        masks = (self.fixed[1],) if self.fixed else self.mask_options
        F = self._features(x, m, gammas)
        self.selection_ = []
        best = (-np.inf, None, None, None)
        for gi, g in enumerate(gammas):
            for use_mask in masks:
                Fi = np.hstack([F[:, gi], Fm]) if use_mask else F[:, gi]
                clf = _ridge().fit(Fi, y)
                score = float(clf[-1].best_score_)  # LOO (GCV) neg-MSE at the selected alpha
                self.selection_.append(dict(gamma=g, mask=use_mask, loo_score=score, alpha=float(clf[-1].alpha_)))
                if score > best[0]:
                    best = (score, g, use_mask, clf)
        _, self.gamma_, self.use_mask_, self.clf_ = best
        self.n_features_ = int(self.biases_.shape[0] + (self.mask_features // NUM_KERNELS * NUM_KERNELS if self.use_mask_ else 0))
        return self

    def decision_function(self, X):
        x, m = self._prep(X)
        F = self._features(x, m, (self.gamma_,))[:, 0]
        if self.use_mask_:
            F = np.hstack([F, self.mask_rocket_.transform(m)])
        s = self.clf_.decision_function(F)
        return np.stack([-s, s], axis=1) if s.ndim == 1 else s

    @property
    def classes_(self):
        return self.clf_.classes_


class MissRocketMV:
    """Channel-wise multivariate MissRocket (independent per-channel transforms, joint ridge head).

    X: (n, D, L) with NaN. `num_features` is the per-channel budget. Selection of (gamma, mask) is
    joint across channels using the same ridge LOO criterion. With `fixed`, no selection is done.
    `conv='group_mean'` gives the native (no-imputation) MaskRocket baseline instead.
    """

    def __init__(self, num_features=504, gammas=DEFAULT_GAMMAS, mask_options=(False, True), mask_features=168,
                 random_state=None, fixed=(1.0, False), conv="imputed"):
        self.num_features = num_features
        self.gammas = tuple(gammas)
        self.mask_options = tuple(mask_options)
        self.mask_features = mask_features
        self.random_state = random_state
        self.fixed = fixed
        self.conv = conv

    def _chan(self, X, d):
        Xd = np.asarray(X[:, d, :], dtype=np.float32)
        M = (~np.isnan(Xd)).astype(np.float32)
        return np.ascontiguousarray(impute_linear(Xd)), np.ascontiguousarray(M), Xd

    def _value_features(self, X, gammas):
        out = []
        for d in range(X.shape[1]):
            x, m, raw = self._chan(X, d)
            if self.conv == "imputed":
                out.append(_transform_hist(x, m, self.dil_[d], self.nfpd_[d], self.bias_[d], _wtab(gammas)))
            else:
                F = self.native_[d].transform(raw)
                out.append(np.repeat(F[:, None, :], len(gammas), axis=1))
        return np.concatenate(out, axis=2)  # (n, G, D*f)

    def _mask_features(self, X):
        return np.hstack([self.mrk_[d].transform((~np.isnan(X[:, d, :])).astype(np.float32)) for d in range(X.shape[1])])

    def fit(self, X, y):
        rng = np.random.RandomState(self.random_state)
        D, L = X.shape[1], X.shape[2]
        self.dil_, self.nfpd_, self.bias_, self.native_, self.mrk_ = [], [], [], [], []
        for d in range(D):
            x, m, raw = self._chan(X, d)
            dl, nf = _fit_dilations(L, self.num_features, 32)
            q = _quantiles(NUM_KERNELS * int(np.sum(nf)))
            self.dil_.append(dl); self.nfpd_.append(nf)
            if self.conv == "imputed":
                self.bias_.append(_fit_biases(x, m, dl, nf, q, CONV_MODES["imputed"], 0, _wtab([1.0])[0],
                                              np.float32(1.0), int(rng.randint(2**31 - 1))))
            else:
                self.native_.append(MaskRocket(num_features=self.num_features, conv=self.conv, pooling="support",
                                               random_state=int(rng.randint(2**31 - 1))).fit(raw))
        gammas = (self.fixed[0],) if self.fixed else (self.gammas if self.conv == "imputed" else (0.0,))
        masks = (self.fixed[1],) if self.fixed else self.mask_options
        if any(masks):
            for d in range(D):
                mm = (~np.isnan(X[:, d, :])).astype(np.float32)
                self.mrk_.append(MaskRocket(num_features=self.mask_features, conv="zero_fill", pooling="all",
                                            random_state=int(rng.randint(2**31 - 1))).fit(mm))
            Fm = self._mask_features(X)
        F = self._value_features(X, gammas)
        self.selection_, best = [], (-np.inf, None, None, None)
        for gi, g in enumerate(gammas):
            for use_mask in masks:
                Fi = np.hstack([F[:, gi], Fm]) if use_mask else F[:, gi]
                clf = _ridge().fit(Fi, y)
                sc = float(clf[-1].best_score_)
                self.selection_.append(dict(gamma=g, mask=use_mask, loo_score=sc))
                if sc > best[0]:
                    best = (sc, g, use_mask, clf)
        _, self.gamma_, self.use_mask_, self.clf_ = best
        self.n_features_ = F.shape[2] + (Fm.shape[1] if self.use_mask_ else 0)
        return self

    def decision_function(self, X):
        F = self._value_features(X, (self.gamma_,))[:, 0]
        if self.use_mask_:
            F = np.hstack([F, self._mask_features(X)])
        s = self.clf_.decision_function(F)
        return np.stack([-s, s], axis=1) if s.ndim == 1 else s

    @property
    def classes_(self):
        return self.clf_.classes_
