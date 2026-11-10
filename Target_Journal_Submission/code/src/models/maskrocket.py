"""MaskRocket: a missingness-aware MiniRocket transform (numba implementation).

Notation (per series): x in R^L with observation mask m in {0,1}^L (1 = observed).
MiniRocket (Dempster et al. 2021) uses 84 kernels of length 9 whose weights are
-1 at six taps Q and +2 at three taps P. Because the weights sum to zero,

    C(t) = 2 * S_P(t) - S_Q(t) = 6 * ( mean_P x - mean_Q x ).

MaskRocket estimates this response from the observed taps only (component A):

    C_hat(t) = (6 / n_P) * S^obs_P(t) - (6 / n_Q) * S^obs_Q(t),

with n_P, n_Q the numbers of observed taps in P and Q. C_hat is defined
("supported") when n_P >= 1, n_Q >= 1 and n_P + n_Q >= ceil(s_min * 9).
Out-of-bounds taps under zero padding are observed zeros, exactly as in
MiniRocket, so MaskRocket reproduces MiniRocket bit-for-bit on complete data
(tests/test_maskrocket.py).

Component B (support-aware pooling): PPV is computed over supported positions
only. The alternative 'all' divides by the number of all positions, so
unsupported positions count as "not positive" (this mimics how NaNs propagate
through the reference implementation, where NaN > b is False).

Component C (missingness-pattern features): an additional MiniRocket transform
of the binary mask m (``mask_features`` features; 0 disables).

conv modes: 'group_mean' (proposed), 'zero_fill' (standard weights on x*m),
'partial' (partial-convolution rescaling by 9/|O|, Liu et al. 2018).
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
from numba import njit, prange

_INDICES = np.array(list(combinations(range(9), 3)), dtype=np.int64)  # (84, 3)
_QIND = np.array([[j for j in range(9) if j not in row] for row in _INDICES], dtype=np.int64)  # (84, 6)
NUM_KERNELS = 84
CONV_MODES = {"group_mean": 0, "zero_fill": 1, "partial": 2, "imputed": 3}


def _fit_dilations(input_length: int, num_features: int, max_dilations_per_kernel: int = 32):
    """Identical to the reference MiniRocket implementation."""
    num_features_per_kernel = num_features // NUM_KERNELS
    true_max = min(num_features_per_kernel, max_dilations_per_kernel)
    multiplier = num_features_per_kernel / true_max
    max_exponent = np.log2((input_length - 1) / (9 - 1))
    dilations, num_features_per_dilation = np.unique(
        np.logspace(0, max_exponent, true_max, base=2).astype(np.int32), return_counts=True)
    num_features_per_dilation = (num_features_per_dilation * multiplier).astype(np.int32)
    remainder = num_features_per_kernel - np.sum(num_features_per_dilation)
    i = 0
    while remainder > 0:
        num_features_per_dilation[i] += 1
        remainder -= 1
        i = (i + 1) % len(num_features_per_dilation)
    return dilations.astype(np.int64), num_features_per_dilation.astype(np.int64)


def _quantiles(n: int) -> np.ndarray:
    return np.array([(k * ((np.sqrt(5) + 1) / 2)) % 1 for k in range(1, n + 1)], dtype=np.float32)


@njit(cache=True)
def _taps(x, m, d, mode, V, O):
    """Shifted tap arrays for one dilation: V[j,t] = value at tap j (0 if unobserved unless
    mode==3), O[j,t] = 1 if tap j observed (out-of-bounds taps = observed zeros)."""
    L = x.shape[0]
    for j in range(9):
        off = (j - 4) * d
        for t in range(L):
            idx = t + off
            if idx < 0 or idx >= L:
                V[j, t] = 0.0
                O[j, t] = 1.0
            elif m[idx] > 0:
                V[j, t] = x[idx]
                O[j, t] = 1.0
            else:
                V[j, t] = x[idx] if mode == 3 else 0.0
                O[j, t] = 0.0


_RECIP6 = np.array([0.0, 6.0, 3.0, 2.0, 1.5, 1.2, 1.0], dtype=np.float32)  # 6/n, n = 0..6


@njit(cache=True)
def _responses(V, O, k, mode, min_obs, gamma, C, S):
    """Fill C[t] (response) and S[t] (pooling weight) for kernel k from precomputed taps.

    mode 0 group_mean: C = (6/n_P) S_P - (6/n_Q) S_Q over observed taps; S = 1 if supported.
    mode 1 zero_fill : C = 2 S_P - S_Q on zero-filled values; S = 1.
    mode 2 partial   : C = (2 S_P - S_Q) * 9/|O|; S = 1 if |O| >= 1.
    mode 3 imputed   : C = 2 S_P - S_Q on gap-filled values; S = gamma[|O|] = (|O|/9)**g (lookup table).
    (Branch-free loops per mode so that LLVM can vectorise them.)
    """
    L = C.shape[0]
    p0 = _INDICES[k, 0]; p1 = _INDICES[k, 1]; p2 = _INDICES[k, 2]
    q0 = _QIND[k, 0]; q1 = _QIND[k, 1]; q2 = _QIND[k, 2]; q3 = _QIND[k, 3]; q4 = _QIND[k, 4]; q5 = _QIND[k, 5]
    two = np.float32(2.0)
    if mode == 1:
        for t in range(L):
            C[t] = two * (V[p0, t] + V[p1, t] + V[p2, t]) - (V[q0, t] + V[q1, t] + V[q2, t] + V[q3, t] + V[q4, t] + V[q5, t])
            S[t] = 1.0
    elif mode == 0:
        for t in range(L):
            sp = V[p0, t] + V[p1, t] + V[p2, t]
            sq = V[q0, t] + V[q1, t] + V[q2, t] + V[q3, t] + V[q4, t] + V[q5, t]
            cp = np.int64(O[p0, t] + O[p1, t] + O[p2, t])
            cq = np.int64(O[q0, t] + O[q1, t] + O[q2, t] + O[q3, t] + O[q4, t] + O[q5, t])
            ok = (cp >= 1) & (cq >= 1) & (cp + cq >= min_obs)
            C[t] = (_RECIP6[cp] * sp - _RECIP6[cq] * sq) if ok else np.float32(0.0)
            S[t] = np.float32(1.0) if ok else np.float32(0.0)
    elif mode == 2:
        for t in range(L):
            sp = V[p0, t] + V[p1, t] + V[p2, t]
            sq = V[q0, t] + V[q1, t] + V[q2, t] + V[q3, t] + V[q4, t] + V[q5, t]
            n = O[p0, t] + O[p1, t] + O[p2, t] + O[q0, t] + O[q1, t] + O[q2, t] + O[q3, t] + O[q4, t] + O[q5, t]
            ok = n >= 1
            C[t] = (two * sp - sq) * (np.float32(9.0) / max(n, np.float32(1.0))) if ok else np.float32(0.0)
            S[t] = np.float32(1.0) if ok else np.float32(0.0)
    else:
        for t in range(L):
            C[t] = two * (V[p0, t] + V[p1, t] + V[p2, t]) - (V[q0, t] + V[q1, t] + V[q2, t] + V[q3, t] + V[q4, t] + V[q5, t])
            n = np.int64(O[p0, t] + O[p1, t] + O[p2, t] + O[q0, t] + O[q1, t] + O[q2, t] + O[q3, t] + O[q4, t] + O[q5, t])
            S[t] = gamma[n]


@njit(cache=True)
def _fit_biases(X, M, dilations, nfpd, quantiles, mode, min_obs, gamma, seed):
    np.random.seed(seed)
    n, L = X.shape
    total = 0
    for i in range(dilations.shape[0]):
        total += nfpd[i] * NUM_KERNELS
    biases = np.zeros(total, dtype=np.float32)
    C = np.zeros(L, dtype=np.float32)
    S = np.zeros(L, dtype=np.float32)
    V = np.zeros((9, L), dtype=np.float32)
    O = np.zeros((9, L), dtype=np.float32)
    fs = 0
    for di in range(dilations.shape[0]):
        d = dilations[di]
        nf = nfpd[di]
        for k in range(NUM_KERNELS):
            got = False
            for _try in range(20):
                i = np.random.randint(n)
                _taps(X[i], M[i], d, mode, V, O)
                _responses(V, O, k, mode, min_obs, gamma, C, S)
                cnt = 0
                for t in range(L):
                    if S[t] > 0:
                        cnt += 1
                if cnt > 0:
                    got = True
                    break
            if got:
                vals = np.empty(cnt, dtype=np.float32)
                c = 0
                for t in range(L):
                    if S[t] > 0:
                        vals[c] = C[t]
                        c += 1
                biases[fs:fs + nf] = np.quantile(vals, quantiles[fs:fs + nf])
            fs += nf
    return biases


@njit(parallel=True, cache=True, fastmath=True)
def _transform(X, M, dilations, nfpd, biases, mode, min_obs, gamma, pooling_support):
    n, L = X.shape
    nfeat = biases.shape[0]
    out = np.zeros((n, nfeat), dtype=np.float32)
    for i in prange(n):
        C = np.zeros(L, dtype=np.float32)
        S = np.zeros(L, dtype=np.float32)
        V = np.zeros((9, L), dtype=np.float32)
        O = np.zeros((9, L), dtype=np.float32)
        fs = 0
        for di in range(dilations.shape[0]):
            d = dilations[di]
            nf = nfpd[di]
            pad = ((9 - 1) * d) // 2
            p0 = di % 2
            _taps(X[i], M[i], d, mode, V, O)
            for k in range(NUM_KERNELS):
                _responses(V, O, k, mode, min_obs, gamma, C, S)
                p1 = (p0 + k) % 2
                t0 = 0
                t1 = L
                if p1 == 1 and L > 2 * pad:
                    t0 = pad
                    t1 = L - pad
                den = np.float32(0.0)
                for t in range(t0, t1):
                    den += S[t]
                for f in range(nf):
                    b = biases[fs + f]
                    num = np.float32(0.0)
                    for t in range(t0, t1):
                        num += S[t] * np.float32(C[t] > b)
                    if pooling_support:
                        out[i, fs + f] = np.float64(num) / np.float64(den) if den > 0 else 0.0
                    else:
                        out[i, fs + f] = np.float64(num) / np.float64(t1 - t0)
                fs += nf
    return out


class MaskRocket:
    """Missingness-aware MiniRocket transform for univariate series with NaNs."""

    def __init__(self, num_features: int = 10_000, max_dilations_per_kernel: int = 32,
                 conv: str = "group_mean", pooling: str = "support", s_min: float = 0.0,
                 mask_features: int = 0, random_state: int | None = None, gamma: float = 1.0):
        self.gamma = gamma
        self.num_features = num_features
        self.max_dilations_per_kernel = max_dilations_per_kernel
        self.conv = conv
        self.pooling = pooling
        self.s_min = s_min
        self.mask_features = mask_features
        self.random_state = random_state

    def _to_xm(self, X):
        X = np.asarray(X, dtype=np.float32)
        if X.ndim == 3:
            X = X[:, 0, :]
        M = (~np.isnan(X)).astype(np.float32)
        if self.conv == "imputed":
            from src.preprocessing.imputation import impute_linear
            V = impute_linear(X)
        else:
            V = np.nan_to_num(X, nan=0.0)
        return np.ascontiguousarray(V, dtype=np.float32), np.ascontiguousarray(M)

    def _wtable(self):
        """Pooling-weight lookup (k/9)**gamma for k = 0..9 observed taps (mode 'imputed')."""
        k = np.arange(10, dtype=np.float64) / 9.0
        return (k ** self.gamma if self.gamma != 0 else np.ones(10)).astype(np.float32)

    def _min_obs(self):
        return int(np.ceil(self.s_min * 9 - 1e-9))

    def fit(self, X, y=None):
        x, m = self._to_xm(X)
        n, L = x.shape
        if L < 9:
            raise ValueError("series length must be >= 9")
        rng = np.random.RandomState(self.random_state)
        self.dilations_, self.nfpd_ = _fit_dilations(L, self.num_features, self.max_dilations_per_kernel)
        q = _quantiles(NUM_KERNELS * int(np.sum(self.nfpd_)))
        self.biases_ = _fit_biases(x, m, self.dilations_, self.nfpd_, q, CONV_MODES[self.conv],
                                   self._min_obs(), self._wtable(), int(rng.randint(2**31 - 1)))
        if self.mask_features > 0:
            self.mask_rocket_ = MaskRocket(num_features=self.mask_features, conv="zero_fill", pooling="all",
                                           random_state=int(rng.randint(2**31 - 1)))
            self.mask_rocket_.fit(m)
        return self

    def transform(self, X):
        x, m = self._to_xm(X)
        F = _transform(x, m, self.dilations_, self.nfpd_, self.biases_, CONV_MODES[self.conv],
                       self._min_obs(), self._wtable(), self.pooling == "support")
        if self.mask_features > 0:
            F = np.concatenate([F, self.mask_rocket_.transform(m)], axis=1)
        return F

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    @property
    def n_features_(self):
        return int(self.biases_.shape[0]) + (self.mask_features // NUM_KERNELS * NUM_KERNELS if self.mask_features else 0)
