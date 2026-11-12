"""E1: main benchmark (matched train/test missingness) incl. baselines and ablations."""
from common import CFG, confirmatory_datasets, quick_datasets, out, log, subset30
from src.training.runner import run_settings


def run(mode="full", seeds=None):
    c, e = CFG["common"], CFG["E1_main"]
    if mode == "quick":
        ds, seeds, rates, mechs = quick_datasets(), [0], [0.5], c["mechanisms"]
    else:
        seeds = seeds if seeds is not None else [0]
        ds, rates, mechs = (confirmatory_datasets() if seeds == [0] else subset30()), c["rates"], c["mechanisms"]
    # order: seed-major so that a partially finished run already covers all datasets for seed 0
    settings = [(d, m, r, r, s) for s in seeds for m in mechs for r in rates for d in ds]
    run_settings(settings, e["methods"], out(f"{mode}/E1_main/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")


def run_seed2(mode="full"):
    if mode != "quick":
        run(mode, seeds=CFG["E1_seed2"]["seeds"])
