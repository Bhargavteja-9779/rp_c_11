"""Development-set screening (dev datasets only; never used for confirmatory claims).

Screening subset: the 8 development datasets with < 2M points (CinCECGTorso and
MixedShapesSmallTrain excluded from screening for compute reasons; CinCECGTorso
partial results from the first screening run are retained in the same CSV).
"""
import sys; sys.path.insert(0, ".")
import pandas as pd
from src.training.runner import run_settings
reg = pd.read_csv("data/registry.csv")
dev = reg[(reg.split == "development") & (reg.points < 2e6)].dataset.tolist()
methods = ["GapRocket", "GapRocket-noC", "MaskRocket", "MaskRocket-noC", "WRocket-noC", "MiniRocket+linear",
           "MiniRocket+linear+mask", "MiniRocket+zero", "LightGBM-NaN", "1NN-ED+linear"]
settings = [(d, m, r, r, 0) for d in dev for m in ["mcar", "block", "mnar"] for r in [0.3, 0.6]]
run_settings(settings, methods, "results/dev/dev_viability.csv",
             log=lambda s: None if s.startswith("Trace") else print(s, flush=True))
