"""Reproducibility audit: re-run a sample of stored confirmatory E1 runs from scratch (fresh numba cache,
separate output file) and compare accuracies with the stored raw results."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from src.utils_cache import clear_numba_cache
clear_numba_cache()
from src.training.runner import run_settings
from src.evaluation.io import read_results
OUT = "results/full/reproducibility_check.csv"
if os.path.exists(OUT):
    os.remove(OUT)
sample = [("Coffee", "block", 0.5), ("Wine", "mcar", 0.2), ("BeetleFly", "mnar", 0.8), ("Plane", "block", 0.8)]
methods = ["MissRocket", "MissRocket-g0", "AeonMiniRocket+linear", "AeonMiniRocket+knn", "MaskRocket-noC", "LightGBM-NaN"]
run_settings([(d, m, r, r, 0) for d, m, r in sample], methods, OUT, log=lambda s: None)
new = read_results(OUT)
old = read_results("results/full/E1_main/raw_results.csv")
m = new.merge(old, on=["dataset", "mechanism", "train_rate", "test_rate", "seed", "method"], suffixes=("_rerun", "_stored"))
m["abs_diff"] = (m.accuracy_rerun - m.accuracy_stored).abs()
print(m[["dataset", "mechanism", "test_rate", "method", "accuracy_stored", "accuracy_rerun", "abs_diff"]].to_string(index=False))
print("runs compared:", len(m), "| exact matches:", int((m.abs_diff == 0).sum()), "| max abs diff:", m.abs_diff.max())
m.to_csv("results/full/tables/table_reproducibility_check.csv", index=False)
