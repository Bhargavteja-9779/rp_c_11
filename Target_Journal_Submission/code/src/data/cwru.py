"""CWRU Bearing Data Center, 12 kHz drive-end accelerometer, 10 classes x 4 motor loads (0-3 HP).

Source: https://engineering.case.edu/bearingdatacenter (files listed on the "12k Drive End Bearing Fault Data"
and "Normal Baseline Data" pages). Classes: normal; inner race (IR), ball (B), outer race at 6 o'clock (OR@6)
faults of diameter 0.007", 0.014", 0.021".

Preprocessing (fixed before any experiment):
* Drive-end channel (*_DE_time).
* The normal-baseline files (97-100) are recorded at 48 kHz (Smith and Randall 2015; confirmed by mains-harmonic
  spectral lines at 120/360 Hz under the 48 kHz reading). They are decimated by 4 (zero-phase FIR anti-aliasing)
  to 12 kHz so that no class can be identified from the sampling rate.
* Non-overlapping segments of 1024 samples (85 ms) from the start of each recording, at most 60 per recording.
* Evaluation by leave-one-load-out: train on three loads, test on the fourth. No recording is shared between
  training and test data (avoids the segment-leakage problem of random segment splits).
* Amplitude scaling: global mean/std of the TRAINING segments (observed values only), applied to both splits.
"""
from __future__ import annotations

import os

import numpy as np
import scipy.io as sio
from scipy.signal import decimate

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "cwru")
CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache", "cwru_segments.npz")
SEG_LEN = 1024
MAX_SEG = 60
FILES = {  # class -> file ids for loads 0,1,2,3
    "Normal": [97, 98, 99, 100],
    "IR007": [105, 106, 107, 108], "B007": [118, 119, 120, 121], "OR007@6": [130, 131, 132, 133],
    "IR014": [169, 170, 171, 172], "B014": [185, 186, 187, 188], "OR014@6": [197, 198, 199, 200],
    "IR021": [209, 210, 211, 212], "B021": [222, 223, 224, 225], "OR021@6": [234, 235, 236, 237],
}
CLASSES = list(FILES)
URL = "https://engineering.case.edu/sites/default/files/{}.mat"


def _signal(fid):
    d = sio.loadmat(os.path.join(ROOT, f"{fid}.mat"))
    key = [k for k in d if k.endswith("DE_time")][0]
    x = d[key].ravel().astype(np.float64)
    if fid in (97, 98, 99, 100):
        x = decimate(x, 4, ftype="fir", zero_phase=True)
    return x


def load_cwru(use_cache=True):
    """Returns X (n, 1024) float32, y (n,), load (n,), recording id (n,)."""
    if use_cache and os.path.exists(CACHE):
        z = np.load(CACHE)
        return z["X"], z["y"], z["load"], z["rec"]
    X, y, load, rec = [], [], [], []
    for ci, c in enumerate(CLASSES):
        for li, fid in enumerate(FILES[c]):
            x = _signal(fid)
            n = min(MAX_SEG, len(x) // SEG_LEN)
            for s in range(n):
                X.append(x[s * SEG_LEN:(s + 1) * SEG_LEN]); y.append(ci); load.append(li); rec.append(fid)
    X, y, load, rec = np.array(X, np.float32), np.array(y), np.array(load), np.array(rec)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez_compressed(CACHE, X=X, y=y, load=load, rec=rec)
    return X, y, load, rec


def fold(test_load, X, y, load):
    tr, te = load != test_load, load == test_load
    mu, sd = float(np.nanmean(X[tr])), float(np.nanstd(X[tr]))
    return ((X[tr] - mu) / sd).astype(np.float32), y[tr], ((X[te] - mu) / sd).astype(np.float32), y[te]
