"""E3: ablations and variants (seed 0, all mechanisms and rates, all confirmatory datasets)."""
from common import CFG, confirmatory_datasets, quick_datasets, out, log
from src.training.runner import run_settings


def run(mode="full"):
    c, e = CFG["common"], CFG["E3_ablation"]
    ds, rates = (quick_datasets(), [0.5]) if mode == "quick" else (confirmatory_datasets(), c["rates"])
    settings = [(d, m, r, r, s) for s in e["seeds"] for m in c["mechanisms"] for r in rates for d in ds]
    run_settings(settings, e["methods"], out(f"{mode}/E3_ablation/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
