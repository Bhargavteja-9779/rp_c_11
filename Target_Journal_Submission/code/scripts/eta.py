"""Progress/ETA of E1 weighted by dataset size (no accuracy values are read)."""
import sys; sys.path.insert(0, "."); sys.path.insert(0, "experiments")
import pandas as pd
from src.evaluation.io import read_results
from common import confirmatory_datasets, CFG
d = read_results("results/full/E1_main/raw_results.csv")
r = pd.read_csv("data/registry.csv").set_index("dataset")
conf = confirmatory_datasets(); nm = len(CFG["E1_main"]["methods"])
tot = r.loc[conf, "points"].sum() * 27 * nm
pts = r.loc[d.dataset, "points"].sum()
d = d[pd.to_datetime(d.timestamp) > pd.Timestamp("2026-11-11T07:40")]
el = (pd.to_datetime(d.timestamp.max()) - pd.to_datetime(d.timestamp.min())).total_seconds()
rate = r.loc[d.dataset, "points"].sum() / max(el, 1)
print(f"E1 done fraction (size-weighted) {pts/tot:.3f}; remaining ≈ {(tot-pts)/rate/3600:.1f} h")
