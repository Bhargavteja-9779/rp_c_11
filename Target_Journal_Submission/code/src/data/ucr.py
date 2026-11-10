"""UCR 2018 univariate archive loading (aeon .ts format)."""
from __future__ import annotations

import os
import numpy as np
from aeon.datasets import load_from_ts_file

DATA_ROOT = os.environ.get("UCR_ROOT", os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "Univariate_ts"))


def _to_array(X):
    """List-of-(1,L_i) or ndarray (n,1,L) -> (n, Lmax) float32, right-padded with NaN."""
    if isinstance(X, np.ndarray):
        return X[:, 0, :].astype(np.float32)
    Lmax = max(x.shape[-1] for x in X)
    out = np.full((len(X), Lmax), np.nan, dtype=np.float32)
    for i, x in enumerate(X):
        out[i, : x.shape[-1]] = x[0]
    return out


def load_ucr(name: str, root: str = DATA_ROOT):
    p = os.path.join(root, name, name)
    Xtr, ytr = load_from_ts_file(p + "_TRAIN.ts")
    Xte, yte = load_from_ts_file(p + "_TEST.ts")
    Xtr, Xte = _to_array(Xtr), _to_array(Xte)
    L = max(Xtr.shape[1], Xte.shape[1])
    if Xtr.shape[1] < L:
        Xtr = np.pad(Xtr, ((0, 0), (0, L - Xtr.shape[1])), constant_values=np.nan)
    if Xte.shape[1] < L:
        Xte = np.pad(Xte, ((0, 0), (0, L - Xte.shape[1])), constant_values=np.nan)
    classes = np.unique(np.concatenate([ytr, yte]))
    cmap = {c: i for i, c in enumerate(classes)}
    return Xtr, np.array([cmap[c] for c in ytr]), Xte, np.array([cmap[c] for c in yte])


def list_datasets(root: str = DATA_ROOT):
    return sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
