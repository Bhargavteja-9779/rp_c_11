"""Development-set viability check (dev datasets only; not used for confirmatory claims)."""
import sys; sys.path.insert(0, ".")
import pandas as pd
from src.training.runner import run_settings
reg = pd.read_csv("data/registry.csv"); dev = reg[reg.split == "development"].dataset.tolist()
methods = ["MaskRocket", "MaskRocket-noC", "MaskRocket-noB", "MaskRocket-noA", "MaskRocket-partialA", "WRocket", "WRocket-noC", "WRocket-g2", "WRocket-g4", "MiniRocket+zero", "MiniRocket+linear", "MiniRocket+linear+mask", "LightGBM-NaN", "1NN-ED+linear"]
settings = [(d, m, r, r, 0) for d in dev for m in ["mcar", "block", "mnar"] for r in [0.3, 0.6]]
run_settings(settings, methods, "results/dev/dev_viability.csv", log=lambda s: None if s.startswith("Trace") else print(s, flush=True))
