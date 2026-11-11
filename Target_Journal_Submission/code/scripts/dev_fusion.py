"""Development-set screening of the fusion hypothesis (dev datasets < 2M points only)."""
import sys; sys.path.insert(0, ".")
import pandas as pd
from src.training.runner import run_settings
reg = pd.read_csv("data/registry.csv")
dev = reg[(reg.split == "development") & (reg.points < 2e6)].dataset.tolist()
methods = ["FusionRocket", "FusionRocket+mask", "MiniRocket20k+linear"]
settings = [(d, m, r, r, 0) for d in dev for m in ["mcar", "block", "mnar"] for r in [0.3, 0.6]]
run_settings(settings, methods, "results/dev/dev_viability.csv",
             log=lambda s: None if s.startswith("Trace") else print(s, flush=True))
