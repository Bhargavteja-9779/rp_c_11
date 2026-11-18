"""E9 diagnostic: where do the errors go under train-complete -> test-with-outages shift?
Re-runs selected (fold, scenario, method) settings of E9 with identical masks and seeds, checks that the stored accuracy is
reproduced, and records the fraction of FAULT segments predicted as 'Normal' (missed faults) plus the full confusion matrix.
Output: results/full/tables/table_e9_confusion.csv
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("AEON_CHUNK", "300")
from sklearn.metrics import accuracy_score, confusion_matrix  # noqa: E402
from src.data.cwru import fold, load_cwru  # noqa: E402
from src.data.missingness import apply_missingness  # noqa: E402
from src.models.methods import run_method  # noqa: E402


def hseed(*p):
    return int(hashlib.sha256("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def main():
    raw = pd.read_csv(os.path.join(ROOT, "results", "full", "E9_cwru", "raw_results.csv"))
    X, y, load, _ = load_cwru()
    rows = []
    for fo in range(4):
        Xtr, ytr, Xte0, yte = fold(fo, X, y, load)
        for cond, mech, rate in [("shift_outage_long30", "block@4096", 0.3), ("shift_outage_medium30", "block@128", 0.3)]:
            Xte = apply_missingness(Xte0, rate, mech, hseed("cwru", fo, cond, 0, "test"))
            for m in ["AeonMiniRocket+linear", "MissRocket", "MaskRocket-noC"]:
                p = run_method(m, Xtr, ytr, Xte, 0)["pred"]
                st = raw[(raw.fold == fo) & (raw.condition == cond) & (raw.seed == 0) & (raw.method == m)]
                fault = yte != 0
                rows.append(dict(fold=fo, condition=cond, method=m, accuracy=accuracy_score(yte, p),
                                 stored_accuracy=float(st.accuracy.iloc[0]) if len(st) else np.nan,
                                 fault_as_normal=float(np.mean(p[fault] == 0)),
                                 confusion=json.dumps(confusion_matrix(yte, p, labels=np.arange(10)).tolist())))
                print(rows[-1]["fold"], cond, m, round(rows[-1]["accuracy"], 4), rows[-1]["stored_accuracy"], round(rows[-1]["fault_as_normal"], 3), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "full", "tables", "table_e9_confusion.csv"), index=False)


if __name__ == "__main__":
    main()
