"""Reproduce the full study.

    python run_all.py --mode quick     # pipeline check: 3 small datasets, 1 seed (~5-10 min on 4 cores)
    python run_all.py --mode full      # complete pre-registered experiments (many CPU hours; resumable)

Steps: (1) data check/preparation, (2) clear numba caches, (3) experiments E1, E3, E5a, E5b, E4, E7, E2,
(4) statistics, tables and figures via scripts/analyze.py. Every experiment appends to CSV/JSONL files
under results/<mode>/ and skips already-finished runs, so an interrupted run can simply be restarted.
Use --only E1,E5_p12 to run a subset, and --skip-experiments to only regenerate statistics/tables/figures.
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))

EXPERIMENTS = [("E1", "e1_main"), ("E5_natural", "e5_natural"), ("E3", "e3_ablation"), ("E4", "e4_shift"),
               ("E5_p12", "e5_p12"), ("E7", "e7_sensitivity"), ("E2", "e2_deep"), ("E4b", "e4b_mechanism_shift"), ("E1_seed2", "e1_main:run_seed2")]


def check_data():
    ucr = os.path.join(ROOT, "data", "raw", "Univariate_ts")
    p12 = os.path.join(ROOT, "data", "raw", "physionet2012")
    if not os.path.isdir(ucr) or not os.path.isdir(p12):
        print("Data missing -> running scripts/download_data.sh", flush=True)
        subprocess.check_call(["bash", os.path.join(ROOT, "scripts", "download_data.sh")])
    reg = os.path.join(ROOT, "data", "registry.csv")
    if not os.path.exists(reg):
        subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "build_registry.py")], cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-experiments", action="store_true")
    a = ap.parse_args()
    os.chdir(ROOT)
    check_data()
    from src.utils_cache import clear_numba_cache
    print(f"cleared {clear_numba_cache()} numba cache files", flush=True)
    only = set(x for x in a.only.split(",") if x)
    if not a.skip_experiments:
        for name, mod in EXPERIMENTS:
            if only and name not in only:
                continue
            t = time.time()
            print(f"=== {name} ({a.mode}) ===", flush=True)
            modname, _, fn = mod.partition(":")
            getattr(__import__(modname), fn or "run")(a.mode)
            print(f"=== {name} done in {time.time() - t:.0f}s ===", flush=True)
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "analyze.py"), "--mode", a.mode], cwd=ROOT)
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "figure_method.py"), a.mode], cwd=ROOT)
    if os.path.exists(os.path.join(ROOT, "results", a.mode, "E1_main", "raw_results.csv")):
        subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "error_analysis.py"), a.mode], cwd=ROOT)


if __name__ == "__main__":
    main()
