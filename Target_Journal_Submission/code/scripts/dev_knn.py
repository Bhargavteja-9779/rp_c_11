"""Dev screening of kNN gap filling (dev datasets only)."""
import sys; sys.path.insert(0, ".")
from src.utils_cache import clear_numba_cache
clear_numba_cache()
import pandas as pd
from src.training.runner import run_settings
reg = pd.read_csv("data/registry.csv")
dev = reg[(reg.split == "development") & (reg.points < 2e6)].dataset.tolist()
settings = [(d, m, r, r, 0) for d in dev for m in ["mcar", "block", "mnar"] for r in [0.3, 0.6]]
run_settings(settings, ["AeonMiniRocket+knn", "MissRocket-knn", "MissRocket-g0-knn"], "results/dev/dev_screening_v2.csv",
             log=lambda s: None if s.startswith("Trace") else print(s, flush=True))
