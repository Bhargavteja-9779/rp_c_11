"""E4b (added in review round 5; post hoc): train/test mechanism shift on the 30-dataset subset, seed 0."""
from common import CFG, quick_datasets, out, log, subset30
from src.training.runner import run_settings


def run(mode="full"):
    e = CFG["E4b_mechanism_shift"]
    ds = quick_datasets() if mode == "quick" else subset30()
    settings = [(d, mech, r, r, 0) for mech, r in e["pairs"] for d in ds]
    run_settings(settings, e["methods"], out(f"{mode}/E4b_mechanism_shift/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
