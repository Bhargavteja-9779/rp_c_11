"""Shared helpers for experiment scripts."""
import os
import sys

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

CFG = yaml.safe_load(open(os.path.join(ROOT, "config", "experiments.yaml")))
REG = pd.read_csv(os.path.join(ROOT, "data", "registry.csv"))


def confirmatory_datasets():
    e = CFG["common"]["eligibility"]
    r = REG[(REG.split == "confirmatory") & (REG.points <= e["max_points"]) & (REG.n_train <= e["max_train"])]
    return r.dataset.tolist()


def excluded_confirmatory():
    keep = set(confirmatory_datasets())
    return REG[(REG.split == "confirmatory") & ~REG.dataset.isin(keep)].dataset.tolist()


def natural_datasets():
    return REG[REG.split == "natural"].dataset.tolist()


def quick_datasets():
    # development datasets only (never confirmatory), so quick checks cannot leak into confirmatory analysis
    return ["ECG200", "GunPoint", "ArrowHead"]


def out(path):
    p = os.path.join(ROOT, "results", path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def log(s):
    if not s.startswith("Trace"):
        print(s, flush=True)


def subset30():
    """Pre-declared random subset of 30 eligible confirmatory datasets (amendment 2; seed fixed before results)."""
    conf = confirmatory_datasets()
    return sorted(np.random.RandomState(CFG["subset30_seed"]).choice(conf, 30, replace=False).tolist())
