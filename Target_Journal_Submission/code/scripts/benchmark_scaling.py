"""Controlled scaling benchmark (review round 6): transform wall time and peak memory vs series length and
number of series, measured in isolated subprocesses on an otherwise idle machine.

Synthetic random-walk series with 50% block missingness (fixed seed). Transform only (fit on n series +
transform the same n series), no classifier, so that the cost of the feature extraction is isolated.
Each measurement: median of 3 repeats after one warm-up (numba compilation excluded); peak RSS from
resource.getrusage of a fresh subprocess. Output: results/full/tables/table_scaling.csv, figures/Fig_scaling.png
"""
import json
import os
import subprocess
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

WORKER = r'''
import sys, json, time, resource, numpy as np
sys.path.insert(0, ROOT)
from src.data.missingness import apply_missingness
from src.preprocessing.imputation import impute_linear
method, n, L = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = np.random.RandomState(0)
X = np.cumsum(rng.randn(n, L), axis=1).astype(np.float32)
X = (X - X.mean(1, keepdims=True)) / (X.std(1, keepdims=True) + 1e-8)
Xm = apply_missingness(X, 0.5, "block", 1)
if method in ("MissRocket", "MissRocket-g0"):
    from src.models.missrocket import MissRocket, _wtab
    from src.models.maskrocket import _fit_dilations, _quantiles, _fit_biases, CONV_MODES, NUM_KERNELS
    g = 1.0 if method == "MissRocket" else 0.0
    def run(A):
        m = MissRocket(random_state=0, fixed=(g, False))
        x, mm = m._prep(A)
        m.dilations_, m.nfpd_ = _fit_dilations(A.shape[1], 10000, 32)
        q = _quantiles(NUM_KERNELS * int(np.sum(m.nfpd_)))
        m.biases_ = _fit_biases(x, mm, m.dilations_, m.nfpd_, q, CONV_MODES["imputed"], 0, _wtab([1.0])[0], np.float32(1.0), 0)
        return m._features(x, mm, (g,))
else:
    from aeon.transformations.collection.convolution_based import MiniRocket, MultiRocket, HydraTransformer
    def run(B):
        Z = impute_linear(B)[:, None, :].astype(np.float64)
        ts = {"MiniRocket+interp": [MiniRocket(random_state=0, n_jobs=4)], "MultiRocket+interp": [MultiRocket(random_state=0, n_jobs=4)],
              "HydraMultiRocket+interp": [HydraTransformer(random_state=0, n_jobs=4), MultiRocket(random_state=0, n_jobs=4)]}[method]
        return [t.fit_transform(Z) for t in ts]
run(Xm[: min(n, 20)])  # warm-up (JIT compilation)
times = []
for _ in range(3):
    s = time.perf_counter(); F = run(Xm); times.append(time.perf_counter() - s)
print(json.dumps(dict(method=method, n=n, L=L, time_s=float(np.median(times)), peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)))
'''.replace("ROOT", repr(ROOT))


def main():
    rows = []
    methods = ["MissRocket", "MissRocket-g0", "MiniRocket+interp", "MultiRocket+interp", "HydraMultiRocket+interp"]
    for n, L in [(200, 128), (200, 512), (200, 2048), (1000, 128), (1000, 512), (1000, 2048)]:
        for m in methods:
            out = subprocess.run([sys.executable, "-c", WORKER, m, str(n), str(L)], capture_output=True, text=True, cwd=ROOT)
            line = [l for l in out.stdout.splitlines() if l.startswith("{")]
            if line:
                r = json.loads(line[-1]); rows.append(r); print(r, flush=True)
            else:
                print("FAILED", m, n, L, out.stderr[-500:], flush=True)
    df = pd.DataFrame(rows)
    tab = os.path.join(ROOT, "results", "full", "tables", "table_scaling")
    df.to_csv(tab + ".csv", index=False)
    with open(tab + ".md", "w") as f:
        f.write(df.to_markdown(index=False, floatfmt=".3f"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter
    fig, axs = plt.subplots(1, 2, figsize=(7.1, 2.6))
    for ax, n in zip(axs, [200, 1000]):
        for m, mk in zip(methods, "osD^v"):
            s = df[(df.method == m) & (df.n == n)].sort_values("L")
            ax.plot(s.L, s.time_s, marker=mk, label=m, lw=1.6 if m == "MissRocket" else 1.0,
                    color="black" if m == "MissRocket" else None)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("series length"); ax.set_title(f"n = {n} series")
        ax.set_xticks([128, 512, 2048]); ax.set_xticklabels(["128", "512", "2048"]); ax.xaxis.set_minor_formatter(NullFormatter())
    axs[0].set_ylabel("transform time (s)"); axs[0].legend(fontsize=6)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(ROOT, "results", "full", "figures", f"Fig_scaling.{ext}"), dpi=300)


if __name__ == "__main__":
    main()
