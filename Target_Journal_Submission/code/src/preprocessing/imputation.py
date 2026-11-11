"""Per-series and cross-series imputation used by baselines.

All imputers operate on (n, L) arrays with NaNs. Per-series imputers use only the
series itself, so there is no train/test leakage. The KNN imputer is fit on the
training set only and then applied to the test set.
"""
from __future__ import annotations

import numpy as np


def impute_zero(X):
    return np.nan_to_num(np.asarray(X, dtype=np.float32), nan=0.0)


def impute_mean(X):
    X = np.array(X, dtype=np.float32, copy=True)
    mu = np.nanmean(X, axis=1, keepdims=True)
    mu = np.nan_to_num(mu, nan=0.0)
    idx = np.isnan(X)
    X[idx] = np.broadcast_to(mu, X.shape)[idx]
    return X


def impute_linear(X):
    """Linear interpolation in time; leading/trailing gaps take the nearest observed value."""
    X = np.array(X, dtype=np.float32, copy=True)
    t = np.arange(X.shape[1])
    for i in range(X.shape[0]):
        obs = ~np.isnan(X[i])
        if obs.all():
            continue
        if obs.sum() == 0:
            X[i] = 0.0
            continue
        X[i, ~obs] = np.interp(t[~obs], t[obs], X[i, obs])
    return X


def impute_locf(X):
    """Last observation carried forward; leading gap filled backward."""
    X = np.array(X, dtype=np.float32, copy=True)
    for i in range(X.shape[0]):
        row = X[i]
        obs = np.flatnonzero(~np.isnan(row))
        if obs.size == 0:
            X[i] = 0.0
            continue
        idx = np.where(~np.isnan(row), np.arange(row.size), 0)
        np.maximum.accumulate(idx, out=idx)
        filled = row[idx]
        filled[: obs[0]] = row[obs[0]]
        X[i] = filled
    return X


class KNNSeriesImputer:
    """sklearn KNNImputer on aligned time points (fit on train, apply to test)."""

    def __init__(self, n_neighbors=5):
        from sklearn.impute import KNNImputer
        self.imp = KNNImputer(n_neighbors=n_neighbors, keep_empty_features=True)

    def fit(self, X):
        self.imp.fit(X)
        return self

    def transform(self, X):
        out = self.imp.transform(X).astype(np.float32)
        return out


IMPUTERS = {"zero": impute_zero, "mean": impute_mean, "linear": impute_linear, "locf": impute_locf}


def resample_prefix(X):
    """For variable-length series stored as NaN-right-padded rows: stretch the observed prefix to the full
    length by linear interpolation (standard equal-length conversion). Rows with interior NaNs are
    linearly imputed instead."""
    X = np.array(X, dtype=np.float32, copy=True)
    L = X.shape[1]
    for i in range(X.shape[0]):
        obs = ~np.isnan(X[i])
        if obs.all():
            continue
        last = np.flatnonzero(obs)
        if last.size == 0:
            X[i] = 0.0
            continue
        k = last[-1] + 1
        if obs[:k].all():  # pure trailing padding
            X[i] = np.interp(np.linspace(0, k - 1, L), np.arange(k), X[i, :k])
        else:
            X[i] = impute_linear(X[i:i + 1])[0]
    return X


IMPUTERS["resample"] = resample_prefix
