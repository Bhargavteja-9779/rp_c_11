"""E5a: naturally incomplete / variable-length UCR datasets (no simulated missingness; rate 0)."""
from common import CFG, natural_datasets, out, log
from src.training.runner import run_settings


def run(mode="full"):
    ds = natural_datasets()[:2] if mode == "quick" else natural_datasets()
    seeds = [0] if mode == "quick" else CFG["common"]["seeds"]
    settings = [(d, "mcar", 0.0, 0.0, s) for s in seeds for d in ds]  # rate 0 => data used as distributed
    run_settings(settings, CFG["E5_natural"]["methods"], out(f"{mode}/E5_natural/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
