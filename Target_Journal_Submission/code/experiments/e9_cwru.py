"""E9 (added after external review; design fixed and committed before any run): industrial case study,
CWRU bearing vibration data with simulated sensor dropouts.

Folds: leave-one-load-out (4). Seeds: 0, 1 (missingness masks and transform randomness).
Conditions: see config/experiments.yaml (E9_cwru). Outputs one CSV row per fold x condition x seed x method,
including per-class recall (JSON) for per-class / fault-class analysis.
"""
import csv
import hashlib
import json
import os
import time
import traceback

import numpy as np
from common import CFG, out, log
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, recall_score

from src.data.cwru import CLASSES, fold, load_cwru
from src.data.missingness import apply_missingness
from src.models.methods import run_method

FIELDS = ["fold", "condition", "train_mech", "train_rate", "test_mech", "test_rate", "seed", "method", "accuracy",
          "balanced_accuracy", "macro_f1", "per_class_recall", "fit_s", "predict_s", "n_features", "train_obs_frac",
          "test_obs_frac", "status", "timestamp"]


def hseed(*p):
    return int(hashlib.sha256("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def run(mode="full"):
    os.environ.setdefault("AEON_CHUNK", "300")
    e = CFG["E9_cwru"]
    X, y, load, rec = load_cwru()
    conds = e["conditions"]
    folds, seeds, methods = (([0], [0], e["methods"][:3]) if mode == "quick" else (e["folds"], e["seeds"], e["methods"]))
    if mode == "quick":
        conds = conds[:2]
    path = out(f"{mode}/E9_cwru/raw_results.csv")
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for r in csv.DictReader(f):
                done.add((int(r["fold"]), r["condition"], int(r["seed"]), r["method"]))
    new = not os.path.exists(path)
    fh = open(path, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if new:
        w.writeheader()
    for seed in seeds:
        for fo in folds:
            Xtr0, ytr, Xte0, yte = fold(fo, X, y, load)
            for c in conds:
                ms = methods if seed == 0 or mode == "quick" else [m for m in methods if m in e["seed1_methods"]]
                todo = [m for m in ms if (fo, c["name"], seed, m) not in done]
                if not todo:
                    continue
                Xtr = apply_missingness(Xtr0, c["train_rate"], c["train_mech"], hseed("cwru", fo, c["name"], seed, "train")) if c["train_rate"] > 0 else Xtr0
                Xte = apply_missingness(Xte0, c["test_rate"], c["test_mech"], hseed("cwru", fo, c["name"], seed, "test")) if c["test_rate"] > 0 else Xte0
                for m in todo:
                    row = dict(fold=fo, condition=c["name"], train_mech=c["train_mech"], train_rate=c["train_rate"],
                               test_mech=c["test_mech"], test_rate=c["test_rate"], seed=seed, method=m,
                               train_obs_frac=float((~np.isnan(Xtr)).mean()), test_obs_frac=float((~np.isnan(Xte)).mean()),
                               timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"))
                    try:
                        r = run_method(m, Xtr, ytr, Xte, seed)
                        p = r["pred"]
                        row.update(accuracy=accuracy_score(yte, p), balanced_accuracy=balanced_accuracy_score(yte, p),
                                   macro_f1=f1_score(yte, p, average="macro"),
                                   per_class_recall=json.dumps([float(v) for v in recall_score(yte, p, average=None, labels=np.arange(len(CLASSES)), zero_division=0)]),
                                   fit_s=r["fit_s"], predict_s=r["predict_s"], n_features=r["n_features"], status="ok")
                    except Exception as ex:
                        row.update(status="error: " + repr(ex)[:200])
                        log(traceback.format_exc())
                    w.writerow(row); fh.flush()
                    log(f"CWRU fold{fo} {c['name']} s{seed} {m}: acc={row.get('accuracy', float('nan')):.4f} [{row['status']}]")
    fh.close()


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
