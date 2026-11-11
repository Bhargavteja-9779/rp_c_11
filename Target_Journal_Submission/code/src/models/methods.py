"""Unified interface for the proposed method, its ablations and all baselines.

Every method maps (X_train, y_train, X_test, seed) -> dict(pred, score, fit_s, predict_s, n_features)
where X arrays are (n, L) float32 with NaN for missing values. The same seed is used
for all stochastic components of a method within a run.

Classifier head for all ROCKET-family transforms: StandardScaler + RidgeClassifierCV
(alphas = logspace(-3, 3, 10)), exactly as in the MiniRocket reference code.
"""
from __future__ import annotations

import time

import numpy as np
from sklearn.linear_model import RidgeClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.models.maskrocket import MaskRocket
from src.preprocessing.imputation import IMPUTERS, KNNSeriesImputer

MASK_FEATURES = 1000  # mask-pattern features (component C)


def _ridge():
    return make_pipeline(StandardScaler(), RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)))


def _scores(clf, F):
    s = clf.decision_function(F)
    if s.ndim == 1:
        s = np.stack([-s, s], axis=1)
    return s


# ---------------------------------------------------------------- ROCKET-type
def _rocket_pipeline(Xtr, ytr, Xte, seed, transform_factory, pre=None):
    t0 = time.perf_counter()
    if pre is not None:
        Xtr_p, Xte_p = pre(Xtr, Xte)
    else:
        Xtr_p, Xte_p = Xtr, Xte
    tf = transform_factory(seed)
    Ftr = tf.fit_transform(Xtr_p)
    clf = _ridge().fit(Ftr, ytr)
    t1 = time.perf_counter()
    Fte = tf.transform(Xte_p)
    s = _scores(clf, Fte)
    t2 = time.perf_counter()
    return dict(pred=clf.classes_[s.argmax(1)], score=s, fit_s=t1 - t0, predict_s=t2 - t1, n_features=Ftr.shape[1])


def _per_series(imp):
    f = IMPUTERS[imp]
    return lambda a, b: (f(a), f(b))


def _knn_pre(a, b):
    imp = KNNSeriesImputer(5).fit(a)
    # columns entirely missing in train are kept (keep_empty_features); residual NaNs -> linear
    A, B = imp.transform(a), imp.transform(b)
    return IMPUTERS["linear"](A), IMPUTERS["linear"](B)


def _with_mask(transform):
    """Concatenate value features (computed on imputed data) with mask-pattern features."""

    class _T:
        def __init__(self, seed):
            self.v = transform(seed)
            self.mk = MaskRocket(num_features=MASK_FEATURES, conv="zero_fill", pooling="all", random_state=seed + 7)

        def fit_transform(self, X):  # X here is a tuple (imputed, raw)
            imp, raw = X
            self.mk.fit((~np.isnan(raw)).astype(np.float32))
            return np.hstack([self.v.fit_transform(imp), self.mk.transform((~np.isnan(raw)).astype(np.float32))])

        def transform(self, X):
            imp, raw = X
            return np.hstack([self.v.transform(imp), self.mk.transform((~np.isnan(raw)).astype(np.float32))])

    return _T


def minirocket(seed):
    # Standard MiniRocket = MaskRocket with zero_fill on complete (imputed) input.
    return MaskRocket(conv="zero_fill", pooling="all", random_state=seed)


def maskrocket_factory(conv="group_mean", pooling="support", mask=True, s_min=0.0, gamma=1.0, tau=1.0):
    def f(seed):
        return MaskRocket(conv=conv, pooling=pooling, s_min=s_min, gamma=gamma, tau=tau,
                          mask_features=MASK_FEATURES if mask else 0, random_state=seed)
    return f


class _Fusion:
    """Feature-level fusion: MiniRocket on linearly interpolated input  ||  group-mean MaskRocket on raw input."""

    def __init__(self, seed, mask=False, num_features=10_000):
        from src.preprocessing.imputation import impute_linear
        self.imp = impute_linear
        self.a = MaskRocket(num_features=num_features, conv="zero_fill", pooling="all", random_state=seed)
        self.b = MaskRocket(num_features=num_features, conv="group_mean", pooling="support",
                            mask_features=MASK_FEATURES if mask else 0, random_state=seed + 1)

    def fit_transform(self, X):
        return np.hstack([self.a.fit_transform(self.imp(X)), self.b.fit_transform(X)])

    def transform(self, X):
        return np.hstack([self.a.transform(self.imp(X)), self.b.transform(X)])


def _aeon_factory(kind):
    def f(seed):
        from aeon.transformations.collection.convolution_based import MultiRocket, MiniRocket, HydraTransformer
        if kind == "multirocket":
            return _Aeon3D(MultiRocket(random_state=seed, n_jobs=4))
        if kind == "aeon_minirocket":
            return _Aeon3D(MiniRocket(random_state=seed, n_jobs=4))
        if kind == "hydra_multirocket":
            return _Concat3D([HydraTransformer(random_state=seed, n_jobs=4), MultiRocket(random_state=seed, n_jobs=4)])
        raise ValueError(kind)
    return f


class _Aeon3D:
    def __init__(self, t):
        self.t = t

    def fit_transform(self, X):
        return np.asarray(self.t.fit_transform(X[:, None, :].astype(np.float64)), dtype=np.float32)

    def transform(self, X):
        return np.asarray(self.t.transform(X[:, None, :].astype(np.float64)), dtype=np.float32)


class _Concat3D:
    def __init__(self, ts):
        self.ts = [_Aeon3D(t) for t in ts]

    def fit_transform(self, X):
        return np.hstack([t.fit_transform(X) for t in self.ts])

    def transform(self, X):
        return np.hstack([t.transform(X) for t in self.ts])


# ---------------------------------------------------------------- MissRocket (final proposed method)
def run_missrocket(Xtr, ytr, Xte, seed, **kw):
    from src.models.missrocket import MissRocket
    t0 = time.perf_counter()
    mr = MissRocket(random_state=seed, **kw).fit(Xtr, ytr)
    t1 = time.perf_counter()
    s = mr.decision_function(Xte)
    t2 = time.perf_counter()
    return dict(pred=mr.classes_[s.argmax(1)], score=s, fit_s=t1 - t0, predict_s=t2 - t1, n_features=mr.n_features_,
                selected_gamma=mr.gamma_, selected_mask=mr.use_mask_)


# ---------------------------------------------------------------- other baselines
def run_1nn_ed(Xtr, ytr, Xte, seed):
    t0 = time.perf_counter()
    A, B = IMPUTERS["linear"](Xtr), IMPUTERS["linear"](Xte)
    t1 = time.perf_counter()
    d = (B ** 2).sum(1)[:, None] + (A ** 2).sum(1)[None, :] - 2 * B @ A.T
    s = np.zeros((len(B), int(ytr.max()) + 1))
    nn = d.argmin(1)
    pred = ytr[nn]
    # class score = -min distance to that class (for AUC)
    for c in np.unique(ytr):
        s[:, c] = -d[:, ytr == c].min(1)
    t2 = time.perf_counter()
    classes = np.unique(ytr)
    return dict(pred=pred, score=s[:, classes], fit_s=t1 - t0, predict_s=t2 - t1, n_features=A.shape[1], classes=classes)


def run_lgbm_nan(Xtr, ytr, Xte, seed):
    import lightgbm as lgb
    t0 = time.perf_counter()
    clf = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, subsample=0.8, subsample_freq=1,
                             colsample_bytree=0.5, min_child_samples=5, random_state=seed, n_jobs=4, verbose=-1)
    clf.fit(Xtr, ytr)
    t1 = time.perf_counter()
    s = clf.predict_proba(Xte)
    t2 = time.perf_counter()
    return dict(pred=clf.classes_[s.argmax(1)], score=s, fit_s=t1 - t0, predict_s=t2 - t1, n_features=Xtr.shape[1])


# ---------------------------------------------------------------- registry
def _rk(factory, pre=None):
    return lambda a, y, b, s: _rocket_pipeline(a, y, b, s, factory, pre)


def _rk_mask(factory, imp):
    f = IMPUTERS[imp]
    return lambda a, y, b, s: _rocket_pipeline(a, y, b, s, _with_mask(factory), pre=lambda A, B: ((f(A), A), (f(B), B)))


METHODS = {
    # proposed + ablations (components: A=group-mean conv, B=support pooling, C=mask features)
    "MaskRocket": _rk(maskrocket_factory("group_mean", "support", True)),
    "MaskRocket-noC": _rk(maskrocket_factory("group_mean", "support", False)),
    "MaskRocket-noB": _rk(maskrocket_factory("group_mean", "all", True)),
    "MaskRocket-noA": _rk(maskrocket_factory("zero_fill", "all", True)),  # zero-fill conv => B irrelevant
    "MaskRocket-noAB-noC": _rk(maskrocket_factory("zero_fill", "all", False)),  # = MiniRocket on zero-filled input
    "MaskRocket-partialA": _rk(maskrocket_factory("partial", "support", True)),
    "MaskRocket-noBC": _rk(maskrocket_factory("group_mean", "all", False)),
    # confidence-weighted variant: linear gap filling + observed-tap-fraction weighted PPV
    "WRocket": _rk(maskrocket_factory("imputed", "support", True, gamma=1.0)),
    "WRocket-noC": _rk(maskrocket_factory("imputed", "support", False, gamma=1.0)),
    "WRocket-g2": _rk(maskrocket_factory("imputed", "support", True, gamma=2.0)),
    "WRocket-g4": _rk(maskrocket_factory("imputed", "support", True, gamma=4.0)),
    # dilation-aware hybrid: interpolate taps in gaps <= tau*d, mask taps in longer gaps
    "GapRocket": _rk(maskrocket_factory("gap_adaptive", "support", True, tau=1.0)),
    "GapRocket-noC": _rk(maskrocket_factory("gap_adaptive", "support", False, tau=1.0)),
    "MissRocket": run_missrocket,
    "MissRocket-g0": lambda a, y, b, s: run_missrocket(a, y, b, s, fixed=(0.0, False)),
    "MissRocket-g1": lambda a, y, b, s: run_missrocket(a, y, b, s, fixed=(1.0, False)),
    "MissRocket-noMaskOpt": lambda a, y, b, s: run_missrocket(a, y, b, s, mask_options=(False,)),
    "MissRocket-g0-mask": lambda a, y, b, s: run_missrocket(a, y, b, s, fixed=(0.0, True)),
    # feature-level fusion of interpolated and observed-tap responses
    "FusionRocket": _rk(lambda seed: _Fusion(seed, mask=False)),
    "FusionRocket+mask": _rk(lambda seed: _Fusion(seed, mask=True)),
    "MiniRocket20k+linear": _rk(lambda seed: MaskRocket(num_features=20_000, conv="zero_fill", pooling="all", random_state=seed),
                                _per_series("linear")),
    # imputation + MiniRocket family
    "MiniRocket+zero": _rk(minirocket, _per_series("zero")),
    "MiniRocket+mean": _rk(minirocket, _per_series("mean")),
    "MiniRocket+linear": _rk(minirocket, _per_series("linear")),
    "MiniRocket+locf": _rk(minirocket, _per_series("locf")),
    "MiniRocket+knn": _rk(minirocket, _knn_pre),
    "MiniRocket+linear+mask": _rk_mask(minirocket, "linear"),
    "MultiRocket+linear": _rk(_aeon_factory("multirocket"), _per_series("linear")),
    "HydraMultiRocket+linear": _rk(_aeon_factory("hydra_multirocket"), _per_series("linear")),
    "AeonMiniRocket+linear": _rk(_aeon_factory("aeon_minirocket"), _per_series("linear")),
    # classical / conventional ML
    "1NN-ED+linear": run_1nn_ed,
    "LightGBM-NaN": run_lgbm_nan,
}


def run_method(name, Xtr, ytr, Xte, seed):
    return METHODS[name](Xtr, ytr, Xte, seed)
