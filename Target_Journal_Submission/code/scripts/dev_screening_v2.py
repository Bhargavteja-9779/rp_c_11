"""Development screening v2: ALL candidate variants under one frozen code version.

Dev datasets with < 2M points (8 datasets), MCAR/block/MNAR at 30% and 60%, seed 0.
Only these results inform design decisions; the confirmatory datasets are untouched.
"""
import sys; sys.path.insert(0, ".")
from src.utils_cache import clear_numba_cache
print("cleared numba cache files:", clear_numba_cache(), flush=True)
import pandas as pd
from src.training.runner import run_settings
reg = pd.read_csv("data/registry.csv")
dev = reg[(reg.split == "development") & (reg.points < 2e6)].dataset.tolist()
methods = ["MissRocket", "MissRocket-g0", "MissRocket-g1", "MissRocket-noMaskOpt", "MissRocket-g0-mask",
           "MaskRocket", "MaskRocket-noC", "MaskRocket-partialA", "GapRocket-noC", "FusionRocket", "MiniRocket20k+linear",
           "AeonMiniRocket+linear", "AeonMiniRocket+zero", "LightGBM-NaN", "1NN-ED+linear"]
settings = [(d, m, r, r, 0) for d in dev for m in ["mcar", "block", "mnar"] for r in [0.3, 0.6]]
run_settings(settings, methods, "results/dev/dev_screening_v2.csv",
             log=lambda s: None if s.startswith("Trace") else print(s, flush=True))
