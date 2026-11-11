"""E2: deep missing-aware baseline (GRU-D) on a pre-registered, cost-limited UCR subset."""
from common import CFG, REG, confirmatory_datasets, quick_datasets, out, log
from src.training.runner import run_settings


def run(mode="full"):
    e = CFG["E2_deep"]
    if mode == "quick":
        ds = quick_datasets()[:2]
    else:
        conf = set(confirmatory_datasets())
        ds = REG[REG.dataset.isin(conf) & (REG.length <= e["max_length"]) & (REG.n_train <= e["max_train"])].dataset.tolist()
    settings = [(d, m, r, r, s) for s in e["seeds"] for m in CFG["common"]["mechanisms"] for r in e["rates"] for d in ds]
    run_settings(settings, e["methods"], out(f"{mode}/E2_deep/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
