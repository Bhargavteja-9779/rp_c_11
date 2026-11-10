"""Unit tests for the transform, missingness simulation and imputers."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.missingness import apply_missingness, mask_series  # noqa: E402
from src.models.maskrocket import MaskRocket, _taps, _responses, CONV_MODES  # noqa: E402
from src.preprocessing.imputation import impute_linear, impute_locf, impute_mean  # noqa: E402


def _toy(n=30, L=64, seed=0):
    rng = np.random.RandomState(seed)
    t = np.linspace(0, 6, L)
    X = np.sin(t[None, :] * (1 + rng.rand(n, 1))) + 0.1 * rng.randn(n, L)
    return X.astype(np.float32)


def test_complete_data_equivalence_responses():
    """Proposed estimator == standard MiniRocket kernel response on complete data (bit-exact)."""
    X = _toy()
    x, m = X[0], np.ones(X.shape[1], np.float32)
    for d in [1, 2, 5]:
        V = np.zeros((9, len(x)), np.float32); O = np.zeros_like(V)
        C0 = np.zeros(len(x), np.float32); S0 = np.zeros_like(C0)
        C1 = np.zeros_like(C0); S1 = np.zeros_like(C0)
        g = np.ones(10, np.float32)
        _taps(x, m, d, 0, V, O); _responses(V, O, 7, 0, 0, g, C0, S0)
        _taps(x, m, d, 1, V, O); _responses(V, O, 7, 1, 0, g, C1, S1)
        assert np.array_equal(C0, C1)
        assert S0.min() == 1.0


def test_complete_data_equivalence_features():
    X = _toy()
    a = MaskRocket(conv="group_mean", pooling="support", random_state=1).fit(X).transform(X)
    b = MaskRocket(conv="zero_fill", pooling="support", random_state=1).fit(X).transform(X)
    c = MaskRocket(conv="zero_fill", pooling="all", random_state=1).fit(X).transform(X)
    w = MaskRocket(conv="imputed", pooling="support", random_state=1).fit(X).transform(X)
    assert np.array_equal(a, b)
    assert np.abs(b - c).max() < 1e-6  # 1-ulp differences between two pooling normalisations
    assert np.abs(w - b).max() < 1e-6


def test_offset_invariance_with_missing():
    """Group-mean responses are invariant to adding a constant to the series; zero-fill is not."""
    X = _toy()
    Xm = apply_missingness(X, 0.4, "mcar", seed=3)
    m = MaskRocket(conv="group_mean", pooling="support", random_state=0, num_features=840).fit(Xm)
    f1 = m.transform(Xm)
    f2 = m.transform(Xm + 5.0)
    # responses are offset invariant except at padded borders (observed zeros), so compare
    # features from the no-padding half via a high correlation rather than exact equality
    z = MaskRocket(conv="zero_fill", pooling="all", random_state=0, num_features=840).fit(Xm)
    g1, g2 = z.transform(Xm), z.transform(Xm + 5.0)
    assert np.mean(np.abs(f1 - f2)) < np.mean(np.abs(g1 - g2))


def test_unbiased_under_mcar():
    """E[C_hat | supported] ~= C for a fixed window under MCAR (Monte Carlo)."""
    rng = np.random.RandomState(0)
    x = rng.randn(9).astype(np.float32)
    P = [1, 4, 7]
    Q = [j for j in range(9) if j not in P]
    true = 6 * (x[P].mean() - x[Q].mean())
    est = []
    for _ in range(20000):
        o = rng.rand(9) > 0.4
        if o[P].sum() and o[Q].sum():
            est.append(6 * (x[P][o[P]].mean() - x[Q][o[Q]].mean()))
    assert abs(np.mean(est) - true) < 0.05 * (abs(true) + 1)


@pytest.mark.parametrize("mech", ["mcar", "block", "mnar"])
@pytest.mark.parametrize("r", [0.2, 0.5, 0.8])
def test_missing_rate(mech, r):
    X = _toy(n=200, L=200)
    Xm = apply_missingness(X, r, mech, seed=0)
    frac = np.isnan(Xm).mean()
    assert abs(frac - r) < 0.05, (mech, r, frac)
    assert (np.sum(~np.isnan(Xm), axis=1) >= 2).all()


def test_missingness_deterministic():
    X = _toy()
    a = apply_missingness(X, 0.3, "block", seed=11)
    b = apply_missingness(X, 0.3, "block", seed=11)
    assert np.array_equal(np.isnan(a), np.isnan(b))


def test_imputers():
    x = np.array([[np.nan, 1.0, np.nan, 3.0, np.nan]], np.float32)
    assert np.allclose(impute_linear(x), [[1, 1, 2, 3, 3]])
    assert np.allclose(impute_locf(x), [[1, 1, 1, 3, 3]])
    assert np.allclose(impute_mean(x), [[2, 1, 2, 3, 2]])


def test_handles_all_missing_window():
    X = _toy(n=10, L=50)
    X[:, 10:40] = np.nan
    F = MaskRocket(random_state=0, mask_features=168).fit(X).transform(X)
    assert np.isfinite(F).all()


def test_mask_series_keeps_min():
    rng = np.random.RandomState(0)
    miss = mask_series(np.ones(10, np.float32), 0.999, "mcar", rng)
    assert (~miss).sum() >= 2
