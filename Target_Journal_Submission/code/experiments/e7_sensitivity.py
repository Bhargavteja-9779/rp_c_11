"""E7: sensitivity of MissRocket to the feature budget and to the weighting exponent gamma.

30 confirmatory datasets drawn once with seed 7; block and MCAR at rate 0.5; seed 0.
"""
import numpy as np
from common import CFG, confirmatory_datasets, quick_datasets, out, log

import src.models.methods as M
from src.training.runner import run_settings


def _register():
    e = CFG["E7_sensitivity"]
    names = []
    for nf in e["num_features"]:
        n = f"MissRocket-nf{nf}"
        M.METHODS[n] = (lambda nf_: (lambda a, y, b, s: M.run_missrocket(a, y, b, s, num_features=nf_, fixed=(1.0, False))))(nf)
        names.append(n)
        n0 = f"MissRocket-g0-nf{nf}"
        M.METHODS[n0] = (lambda nf_: (lambda a, y, b, s: M.run_missrocket(a, y, b, s, num_features=nf_, fixed=(0.0, False))))(nf)
        names.append(n0)
    for g in e["gammas"]:
        n = f"MissRocket-gamma{g}"
        M.METHODS[n] = (lambda g_: (lambda a, y, b, s: M.run_missrocket(a, y, b, s, fixed=(g_, False))))(g)
        names.append(n)
    return names


def run(mode="full"):
    e = CFG["E7_sensitivity"]
    names = _register()
    if mode == "quick":
        ds = quick_datasets()[:1]
    else:
        conf = confirmatory_datasets()
        ds = sorted(np.random.RandomState(7).choice(conf, e["n_datasets"], replace=False).tolist())
    settings = [(d, m, 0.5, 0.5, 0) for m in ["block", "mcar"] for d in ds]
    run_settings(settings, names, out(f"{mode}/E7_sensitivity/raw_results.csv"), log=log)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "full")
