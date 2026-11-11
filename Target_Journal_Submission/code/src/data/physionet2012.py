"""PhysioNet/Computing in Cardiology Challenge 2012 (Silva et al. 2012) loader.

12,000 ICU stays (sets a, b, c), first 48 h. Time-varying variables are binned
hourly (mean of measurements in [h, h+1)), giving X of shape (n, 37, 48), with
NaN where no measurement exists, which is naturally informative missingness.
Static descriptors (Age, Gender, Height, ICUType) are returned separately.
Values of -1 are documented as missing in the challenge data and are set to NaN.
Label: In-hospital_death (binary).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "physionet2012")
CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache", "p12_hourly.npz")

TS_VARS = ["Albumin", "ALP", "ALT", "AST", "Bilirubin", "BUN", "Cholesterol", "Creatinine", "DiasABP", "FiO2", "GCS",
           "Glucose", "HCO3", "HCT", "HR", "K", "Lactate", "Mg", "MAP", "MechVent", "Na", "NIDiasABP", "NIMAP",
           "NISysABP", "PaCO2", "PaO2", "pH", "Platelets", "RespRate", "SaO2", "SysABP", "Temp", "TroponinI",
           "TroponinT", "Urine", "WBC", "Weight"]
STATIC = ["Age", "Gender", "Height", "ICUType"]


def _parse(path):
    df = pd.read_csv(path)
    df = df[df.Parameter.notna()]
    h, mnt = df.Time.str.split(":", expand=True).astype(int).T.values
    df = df.assign(minute=h * 60 + mnt)
    static = {}
    for s in STATIC:
        v = df[(df.Parameter == s) & (df.minute == 0)].Value
        static[s] = float(v.iloc[0]) if len(v) else np.nan
    X = np.full((len(TS_VARS), 48), np.nan, dtype=np.float32)
    ts = df[df.Parameter.isin(TS_VARS)].copy()
    ts.loc[ts.Value < 0, "Value"] = np.nan
    ts["hour"] = np.minimum(ts.minute // 60, 47)
    g = ts.groupby(["Parameter", "hour"]).Value.mean()
    idx = {v: i for i, v in enumerate(TS_VARS)}
    for (p, hr), v in g.items():
        if np.isfinite(v):
            X[idx[p], int(hr)] = v
    return X, [static[s] if (static[s] is not None and static[s] >= 0) else np.nan for s in STATIC]


def load_p12(root: str = ROOT, use_cache: bool = True):
    if use_cache and os.path.exists(CACHE):
        z = np.load(CACHE, allow_pickle=False)
        return z["X"], z["S"], z["y"], z["rid"], z["subset"]
    Xs, Ss, ys, rids, subs = [], [], [], [], []
    for sub in "abc":
        out = pd.read_csv(os.path.join(root, f"Outcomes-{sub}.txt")).set_index("RecordID")
        d = os.path.join(root, f"set-{sub}")
        for f in sorted(os.listdir(d)):
            rid = int(f.split(".")[0])
            X, S = _parse(os.path.join(d, f))
            Xs.append(X); Ss.append(S); ys.append(int(out.loc[rid, "In-hospital_death"])); rids.append(rid); subs.append(sub)
    X, S, y = np.stack(Xs), np.array(Ss, np.float32), np.array(ys)
    rid, subset = np.array(rids), np.array(subs)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez_compressed(CACHE, X=X, S=S, y=y, rid=rid, subset=subset)
    return X, S, y, rid, subset
