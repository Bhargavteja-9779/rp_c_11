"""Build data/registry.csv: properties of all 128 UCR datasets + pre-declared dev split."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, ".")
from src.data.ucr import load_ucr, list_datasets
rows = []
for name in list_datasets():
    Xtr, ytr, Xte, yte = load_ucr(name)
    nan_tr, nan_te = np.isnan(Xtr), np.isnan(Xte)
    # variable length: NaNs only as trailing padding
    def trailing_only(M):
        return all((not row.any()) or row[np.argmax(row):].all() for row in M)
    has_nan = nan_tr.any() or nan_te.any()
    varlen = has_nan and trailing_only(nan_tr) and trailing_only(nan_te)
    rows.append(dict(dataset=name, n_train=len(ytr), n_test=len(yte), length=Xtr.shape[1], n_classes=len(np.unique(np.r_[ytr, yte])),
                     nan_frac=float(np.r_[nan_tr.ravel(), nan_te.ravel()].mean()),
                     kind="variable_length" if varlen else ("native_missing" if has_nan else "complete"),
                     points=(len(ytr) + len(yte)) * Xtr.shape[1]))
df = pd.DataFrame(rows)
# Pre-declared development set: 5 pilot datasets + 5 random complete datasets (seed 2026)
pilot = ["ArrowHead", "GunPoint", "ECG200", "Wafer", "ShapesAll"]
rest = sorted(set(df[df.kind == "complete"].dataset) - set(pilot))
rnd = list(np.random.RandomState(2026).choice(rest, 5, replace=False))
df["split"] = np.where(df.dataset.isin(pilot + rnd), "development", np.where(df.kind == "complete", "confirmatory", "natural"))
df.to_csv("data/registry.csv", index=False)
print(df.kind.value_counts().to_string()); print(df.split.value_counts().to_string())
print("dev:", pilot + rnd)
print(df[df.kind != "complete"][["dataset", "kind", "n_train", "n_test", "length", "nan_frac"]].to_string())
print(df.sort_values("points", ascending=False).head(12)[["dataset", "n_train", "n_test", "length", "points"]].to_string())
