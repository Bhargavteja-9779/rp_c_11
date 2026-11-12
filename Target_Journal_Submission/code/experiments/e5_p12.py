"""E5b: PhysioNet/CinC Challenge 2012, in-hospital mortality from the first 48 h (37 hourly variables).

Fixed split: sets a+b (8000 stays) train, set c (4000 stays) test (different patients; no tuning on test).
Standardisation per variable uses training-set statistics only. Static descriptors are not used by any method.
Each method is run with seeds 0,1,2 (kernel/bias randomness, GRU-D initialisation and validation split).
Metrics: AUROC, AUPRC (test set); paired bootstrap of the AUROC difference is computed in the statistics step.
"""
import json
import time

import numpy as np
from common import CFG, out
from sklearn.metrics import average_precision_score, roc_auc_score

from src.data.physionet2012 import load_p12
from src.models.missrocket import MissRocketMV


def _lgbm(Xtr, ytr, Xte, seed):
    import lightgbm as lgb
    clf = lgb.LGBMClassifier(n_estimators=500, learning_rate=0.03, num_leaves=31, subsample=0.8, subsample_freq=1,
                             colsample_bytree=0.5, min_child_samples=20, random_state=seed, n_jobs=4, verbose=-1)
    clf.fit(Xtr.reshape(len(Xtr), -1), ytr)
    return clf.predict_proba(Xte.reshape(len(Xte), -1))[:, 1]


def _mr(Xtr, ytr, Xte, seed, **kw):
    e = CFG["E5_p12"]
    m = MissRocketMV(num_features=e["per_channel_features"], mask_features=e["mask_features_per_channel"],
                     random_state=seed, **kw).fit(Xtr, ytr)
    s = m.decision_function(Xte)
    return s[:, 1] - s[:, 0], dict(gamma=m.gamma_, mask=bool(m.use_mask_), selection=m.selection_)


def _grud(Xtr, ytr, Xte, seed):
    from src.models.grud import run_grud
    r = run_grud(Xtr, ytr, Xte, seed, hidden=64, epochs=60, patience=8)
    s = r["score"]
    return s[:, 1] - s[:, 0], dict(epochs=r["epochs"])


METHODS = {
    "MissRocket": lambda a, y, b, s: _mr(a, y, b, s, fixed=(1.0, False)),
    "MissRocket-g0": lambda a, y, b, s: _mr(a, y, b, s, fixed=(0.0, False)),
    "MissRocket-select": lambda a, y, b, s: _mr(a, y, b, s, fixed=None),
    "MaskRocket-noC": lambda a, y, b, s: _mr(a, y, b, s, fixed=(0.0, False), conv="group_mean"),
    "LightGBM-NaN": lambda a, y, b, s: (_lgbm(a, y, b, s), {}),
    "GRU-D": _grud,
}


def run(mode="full"):
    X, S, y, rid, sub = load_p12()
    tr, te = np.flatnonzero(sub != "c"), np.flatnonzero(sub == "c")
    if mode == "quick":
        tr, te = tr[:800], te[:400]
    mu = np.nanmean(X[tr], axis=(0, 2))
    sd = np.nanstd(X[tr], axis=(0, 2))
    sd = np.where(sd > 0, sd, 1.0)
    Z = ((X - mu[None, :, None]) / sd[None, :, None]).astype(np.float32)
    seeds = [0]  # amendment 2: seed 0 + patient-level bootstrap CIs
    path = out(f"{mode}/E5_p12/raw_results.jsonl")
    done = set()
    try:
        for line in open(path):
            r = json.loads(line); done.add((r["method"], r["seed"]))
    except FileNotFoundError:
        pass
    np.save(out(f"{mode}/E5_p12/y_test.npy"), y[te])
    for seed in seeds:
        for name in CFG["E5_p12"]["methods"]:
            if (name, seed) in done:
                continue
            t0 = time.perf_counter()
            score, info = METHODS[name](Z[tr], y[tr], Z[te], seed)
            dt = time.perf_counter() - t0
            np.save(out(f"{mode}/E5_p12/scores_{name}_s{seed}.npy"), score)
            rec = dict(method=name, seed=seed, auroc=roc_auc_score(y[te], score), auprc=average_precision_score(y[te], score),
                       time_s=dt, n_train=len(tr), n_test=len(te), info=info)
            with open(path, "a") as f:
                f.write(json.dumps(rec, default=float) + "\n")
            print(f"P12 {name} s{seed}: AUROC={rec['auroc']:.4f} AUPRC={rec['auprc']:.4f} ({dt:.0f}s)", flush=True)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
