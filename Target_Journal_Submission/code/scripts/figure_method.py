"""Fig. 1 (pipeline diagram) and Fig. 2 (worked example computed with the actual transform code
on a development-set series: GunPoint training series 0, block missingness 40%, fixed seed)."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from src.data.missingness import apply_missingness  # noqa: E402
from src.data.ucr import load_ucr  # noqa: E402
from src.models.maskrocket import _taps, _responses  # noqa: E402
from src.preprocessing.imputation import impute_linear  # noqa: E402

OUT = os.path.join(ROOT, "results", sys.argv[1] if len(sys.argv) > 1 else "full", "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def pipeline():
    fig, ax = plt.subplots(figsize=(7.1, 2.3))
    ax.set_xlim(0, 12.2); ax.set_ylim(0, 3.2); ax.axis("off")
    W, H, y0 = 1.75, 1.6, 0.55
    boxes = [("Incomplete\nseries $x$\n(NaN = missing)\nmask $m$", 0.1),
             ("Gap filling\n$\\tilde{x}$ = linear\ninterpolation", 2.15),
             ("MiniRocket\nresponses\n$\\tilde{C}_k(t)$ on $\\tilde{x}$", 4.2),
             ("Window\nreliability\n$c(t)$: number of\nobserved taps\n$w=(c/9)^{\\gamma}$", 6.25),
             ("Weighted PPV\n$\\frac{\\sum w\\,1[\\tilde{C}>b]}{\\sum w}$\n(~10k features)", 8.3),
             ("Ridge classifier\n(LOO-selected\npenalty)", 10.35)]
    for txt, x0 in boxes:
        ax.add_patch(FancyBboxPatch((x0, y0), W, H, boxstyle="round,pad=0.05", fc="#f2f2f2", ec="black", lw=0.8))
        ax.text(x0 + W / 2, y0 + H / 2, txt, ha="center", va="center", fontsize=7)
    for (_, a), (_, b) in zip(boxes[:-1], boxes[1:]):
        ax.annotate("", xy=(b - 0.05, y0 + H / 2), xytext=(a + W + 0.05, y0 + H / 2), arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.annotate("", xy=(6.25 + W / 2, y0 + H + 0.08), xytext=(0.1 + W / 2, y0 + H + 0.08),
                arrowprops=dict(arrowstyle="->", lw=0.8, ls="--", connectionstyle="arc3,rad=-0.18"))
    ax.text(3.6, 3.0, "observation mask $m$", fontsize=7, ha="center")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"Fig1_pipeline.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def example():
    Xtr, ytr, _, _ = load_ucr("GunPoint")
    x = Xtr[0:1].astype(np.float32)
    xm = apply_missingness(x, 0.4, "block", seed=3)[0]
    xi = impute_linear(xm[None])[0]
    m = (~np.isnan(xm)).astype(np.float32)
    L, d, k = len(xi), 1, 10
    V = np.zeros((9, L), np.float32); O = np.zeros_like(V)
    C = np.zeros(L, np.float32); S = np.zeros(L, np.float32)
    wt = (np.arange(10) / 9.0).astype(np.float32)
    _taps(xi, m, d, 3, np.float32(1.0), V, O)
    _responses(V, O, k, 3, 0, wt, C, S)
    Vc = np.zeros_like(V); Oc = np.zeros_like(V); Cc = np.zeros(L, np.float32); Sc = np.zeros(L, np.float32)
    _taps(x[0], np.ones(L, np.float32), d, 1, np.float32(1.0), Vc, Oc)
    _responses(Vc, Oc, k, 1, 0, wt, Cc, Sc)
    t = np.arange(L)
    fig, axs = plt.subplots(3, 1, figsize=(7.1, 4.6), sharex=True)
    axs[0].plot(t, x[0], color="0.75", lw=1.0, label="complete series (unknown)")
    axs[0].plot(t, xm, "k.", ms=2.5, label="observed points")
    axs[0].plot(t, xi, color="tab:blue", lw=0.9, ls="--", label="linear interpolation")
    axs[0].legend(fontsize=6, loc="upper left"); axs[0].set_ylabel("value")
    axs[0].set_title("(a) GunPoint series with 40% block missingness", fontsize=8, loc="left")
    axs[1].plot(t, Cc, color="0.75", lw=1.0, label="response on complete series")
    axs[1].plot(t, C, color="tab:blue", lw=0.9, label="response on interpolated series")
    zero = S == 0
    axs[1].scatter(t[zero], C[zero], s=6, color="tab:red", zorder=3, label="windows with no observed tap (c = 0)")
    axs[1].legend(fontsize=6, loc="upper left"); axs[1].set_ylabel(f"C (kernel {k}, d = {d})")
    axs[1].set_title("(b) MiniRocket kernel response", fontsize=8, loc="left")
    axs[2].fill_between(t, S, step="mid", color="tab:green", alpha=0.5)
    axs[2].set_ylim(0, 1.05); axs[2].set_ylabel("weight (c/9)")
    axs[2].set_xlabel("time index")
    axs[2].set_title("(c) Observed-tap weight used in PPV pooling (γ = 1)", fontsize=8, loc="left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"Fig2_worked_example.{ext}"), dpi=300)
    plt.close(fig)
    return float(np.corrcoef(C[S > 0], Cc[S > 0])[0, 1]), float(np.corrcoef(C[S == 0], Cc[S == 0])[0, 1]) if zero.sum() > 2 else None


if __name__ == "__main__":
    pipeline()
    print("corr(response interp vs complete) on windows with c>0 and c=0:", example())
