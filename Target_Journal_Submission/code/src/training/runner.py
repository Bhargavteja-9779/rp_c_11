"""Resumable experiment runner for the UCR missing-data benchmark.

A *setting* is (dataset, mechanism, train_rate, test_rate, seed). The missingness
seed is derived deterministically from (dataset, mechanism, rates, seed) so that every
method sees exactly the same corrupted data; training and test masks use different
seeds. Results are appended as one CSV row per (setting, method).
"""
from __future__ import annotations

import csv
import hashlib
import os
import time
import traceback

import numpy as np

from src.data.missingness import apply_missingness
from src.data.ucr import load_ucr
from src.evaluation.metrics import compute_metrics
from src.models.methods import run_method

FIELDS = ["dataset", "mechanism", "train_rate", "test_rate", "seed", "method", "accuracy", "balanced_accuracy",
          "macro_f1", "auroc", "auprc", "fit_s", "predict_s", "n_features", "train_obs_frac", "test_obs_frac", "selected_gamma", "selected_mask",
          "status", "timestamp"]


def setting_seed(*parts) -> int:
    h = hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()
    return int(h[:8], 16)


def corrupt(dataset, mechanism, train_rate, test_rate, seed, data=None):
    """mechanism may be 'a>b' (train mechanism a, test mechanism b) for mechanism-shift experiments."""
    Xtr, ytr, Xte, yte = data if data is not None else load_ucr(dataset)
    m_tr, m_te = mechanism.split(">") if ">" in mechanism else (mechanism, mechanism)
    Xtr_m = apply_missingness(Xtr, train_rate, m_tr, setting_seed(dataset, m_tr, train_rate, seed, "train"))
    Xte_m = apply_missingness(Xte, test_rate, m_te, setting_seed(dataset, m_te, test_rate, seed, "test"))
    return Xtr_m, ytr, Xte_m, yte


def done_keys(path):
    keys = set()
    if os.path.exists(path):
        with open(path) as f:
            for r in csv.DictReader(f):
                keys.add((r["dataset"], r["mechanism"], float(r["train_rate"]), float(r["test_rate"]), int(r["seed"]), r["method"]))
    return keys


def run_settings(settings, methods, out_csv, log=print):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    done = done_keys(out_csv)
    new = not os.path.exists(out_csv)
    f = open(out_csv, "a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()
    cache = {}
    for (ds, mech, rtr, rte, seed) in settings:
        todo = [m for m in methods if (ds, mech, float(rtr), float(rte), int(seed), m) not in done]
        if not todo:
            continue
        if ds not in cache:
            cache.clear()
            cache[ds] = load_ucr(ds)
        Xtr, ytr, Xte, yte = corrupt(ds, mech, rtr, rte, seed, cache[ds])
        for m in todo:
            row = dict(dataset=ds, mechanism=mech, train_rate=rtr, test_rate=rte, seed=seed, method=m,
                       train_obs_frac=float((~np.isnan(Xtr)).mean()), test_obs_frac=float((~np.isnan(Xte)).mean()),
                       timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"))
            try:
                r = run_method(m, Xtr, ytr, Xte, seed)
                row.update(compute_metrics(yte, r["pred"], r["score"], r.get("classes")))
                row.update(fit_s=r["fit_s"], predict_s=r["predict_s"], n_features=r["n_features"], status="ok",
                           selected_gamma=r.get("selected_gamma", ""), selected_mask=r.get("selected_mask", ""))
            except Exception as e:  # failures are recorded, never silently dropped
                row.update(status="error: " + repr(e)[:200])
                log(traceback.format_exc())
            w.writerow(row)
            f.flush()
            log(f"{ds} {mech} {rtr}/{rte} s{seed} {m}: acc={row.get('accuracy', float('nan')):.4f} [{row['status']}]")
    f.close()
