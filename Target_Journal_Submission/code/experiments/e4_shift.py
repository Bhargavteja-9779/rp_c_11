"""E4: robustness to train/test missingness-rate shift."""
from common import CFG, confirmatory_datasets, quick_datasets, out, log
from src.training.runner import run_settings


def run(mode="full"):
    e = CFG["E4_shift"]
    ds, seeds = (quick_datasets(), [0]) if mode == "quick" else (confirmatory_datasets(), CFG["common"]["seeds"])
    settings = [(d, m, a, b, s) for s in seeds for m in e["mechanisms"] for a, b in e["pairs"] for d in ds]
    run_settings(settings, e["methods"], out(f"{mode}/E4_shift/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
