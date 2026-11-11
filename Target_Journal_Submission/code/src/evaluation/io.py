"""Robust reading of result CSVs whose schema grew over time (extra trailing columns)."""
import csv
import pandas as pd
from src.training.runner import FIELDS


def read_results(path):
    rows = []
    with open(path) as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            names = header if len(row) == len(header) else FIELDS
            rows.append(dict(zip(names, row)))
    df = pd.DataFrame(rows)
    for c in ["train_rate", "test_rate", "accuracy", "balanced_accuracy", "macro_f1", "auroc", "auprc", "fit_s",
              "predict_s", "n_features", "train_obs_frac", "test_obs_frac"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["seed"] = df["seed"].astype(int)
    return df
