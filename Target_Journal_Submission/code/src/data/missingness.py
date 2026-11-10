"""Missingness simulation for univariate time series (applied per series).

Mechanisms (Rubin 1976 terminology):
  * 'mcar'  : each time point is removed independently with probability r.
  * 'block' : contiguous gaps (sensor dropout). Gap lengths ~ Geometric with mean
              max(2, round(gap_frac * L)); gaps are placed uniformly at random until
              the target fraction r is reached (MCAR at the block level).
  * 'mnar'  : self-masking, value-dependent missingness: P(miss_t) = sigmoid(a + k*z_t),
              z_t = per-series standardised value, k = 2, and the intercept a is solved
              per series so the expected missing fraction equals r. High values are
              more likely to be missing (e.g. sensor saturation).
At least `min_keep` points are always kept per series.
"""
from __future__ import annotations

import numpy as np


def _sigmoid(v):
    return 1.0 / (1.0 + np.exp(-v))


def _solve_intercept(z, r, k):
    lo, hi = -30.0, 30.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _sigmoid(mid + k * z).mean() < r:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mask_series(x: np.ndarray, r: float, mechanism: str, rng: np.random.RandomState,
                gap_frac: float = 0.1, mnar_k: float = 2.0, min_keep: int = 2) -> np.ndarray:
    """Return boolean array `missing` of the same length as x (True = removed)."""
    L = x.shape[0]
    valid = ~np.isnan(x)
    miss = np.zeros(L, dtype=bool)
    if r <= 0:
        return miss
    if mechanism == "mcar":
        miss = rng.rand(L) < r
    elif mechanism == "block":
        target = int(round(r * L))
        mean_len = max(2, int(round(gap_frac * L)))
        p = 1.0 / mean_len
        guard = 0
        while miss.sum() < target and guard < 10 * L:
            g = min(rng.geometric(p), target - int(miss.sum())) if miss.sum() < target else 0
            start = rng.randint(0, L)
            miss[start:min(L, start + g)] = True
            guard += 1
    elif mechanism == "mnar":
        xv = np.where(valid, x, np.nanmean(x))
        sd = xv.std()
        z = (xv - xv.mean()) / (sd if sd > 0 else 1.0)
        a = _solve_intercept(z, r, mnar_k)
        miss = rng.rand(L) < _sigmoid(a + mnar_k * z)
    else:
        raise ValueError(mechanism)
    miss &= valid
    # keep at least min_keep observed points
    obs = np.flatnonzero(valid & ~miss)
    if obs.size < min_keep:
        cand = np.flatnonzero(valid)
        keep = rng.choice(cand, size=min(min_keep, cand.size), replace=False)
        miss[keep] = False
    return miss


def apply_missingness(X: np.ndarray, r: float, mechanism: str, seed: int, **kw) -> np.ndarray:
    """X: (n, L) float array (NaN allowed). Returns a copy with simulated NaNs."""
    rng = np.random.RandomState(seed)
    Xm = np.array(X, dtype=np.float32, copy=True)
    for i in range(Xm.shape[0]):
        miss = mask_series(Xm[i], r, mechanism, rng, **kw)
        Xm[i, miss] = np.nan
    return Xm
