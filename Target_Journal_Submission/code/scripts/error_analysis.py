"""E8: error analysis (run after E1).

1. Per-dataset gain of MissRocket over MiniRocket + linear interpolation (seed-averaged) per condition.
2. Association of the gain with dataset properties (Spearman, Holm-corrected within mechanism):
   length, n_train, n_classes, roughness (mean |second difference| / std of complete training series),
   and the realised mean gap length of the simulated test masks (seed 0).
3. Lists of largest wins/losses; dataset-property figure; confusion matrices and per-class recall
   for the largest win and the largest loss (block, rate 0.5, seed 0), obtained by rerunning those cases with
   predictions saved.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from src.data.ucr import load_ucr  # noqa: E402
from src.evaluation.io import read_results  # noqa: E402
from src.statistics.tests import holm  # noqa: E402
from src.training.runner import corrupt  # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else "full"
BASE = os.path.join(ROOT, "results", MODE)
T, F, S = (os.path.join(BASE, x) for x in ("tables", "figures", "statistics"))
for p in (T, F, S):
    os.makedirs(p, exist_ok=True)
REF = "AeonMiniRocket+linear"


def gap_stats(X):
    m = np.isnan(X)
    lens = []
    for row in m:
        d = np.diff(np.r_[0, row.astype(np.int8), 0])
        lens += list(np.flatnonzero(d == -1) - np.flatnonzero(d == 1))
    return float(np.mean(lens)) if lens else 0.0


def main():
    d = read_results(os.path.join(BASE, "E1_main", "raw_results.csv"))
    d = d[(d.status == "ok") & (d.seed == 0)]  # primary analysis: seed 0 on all eligible datasets
    a = d.groupby(["dataset", "mechanism", "test_rate", "method"]).accuracy.mean().unstack()
    g = (a["MissRocket"] - a[REF]).rename("gain").reset_index()
    reg = pd.read_csv(os.path.join(ROOT, "data", "registry.csv")).set_index("dataset")
    props = {}
    for ds in g.dataset.unique():
        Xtr, ytr, Xte, yte = load_ucr(ds)
        rough = np.mean(np.abs(np.diff(Xtr, 2, axis=1)).mean(1) / (Xtr.std(1) + 1e-12))
        props[ds] = dict(length=int(reg.loc[ds, "length"]), n_train=int(reg.loc[ds, "n_train"]),
                         n_classes=int(reg.loc[ds, "n_classes"]), roughness=float(rough))
    P = pd.DataFrame(props).T
    g = g.join(P, on="dataset")
    gl = []
    for (ds, mech, r), _ in g.groupby(["dataset", "mechanism", "test_rate"]):
        Xtr, ytr, Xte, yte = load_ucr(ds)
        _, _, Xm, _ = corrupt(ds, mech, r, r, 0, (Xtr, ytr, Xte, yte))
        gl.append(dict(dataset=ds, mechanism=mech, test_rate=r, mean_gap_len=gap_stats(Xm),
                       rel_gap_len=gap_stats(Xm) / Xm.shape[1]))
    g = g.merge(pd.DataFrame(gl), on=["dataset", "mechanism", "test_rate"])
    g.to_csv(os.path.join(T, "table_error_analysis_per_dataset.csv"), index=False)
    rows = []
    for mech, gg in g.groupby("mechanism"):
        for prop in ["length", "n_train", "n_classes", "roughness", "mean_gap_len", "rel_gap_len"]:
            rho, p = spearmanr(gg[prop].astype(float), gg.gain)
            rows.append(dict(mechanism=mech, property=prop, spearman_rho=rho, p_value=p, n=len(gg)))
    C = pd.DataFrame(rows)
    C["p_holm_within_mechanism"] = C.groupby("mechanism").p_value.transform(lambda p: holm(p.values))
    C.to_csv(os.path.join(T, "table_error_analysis_correlations.csv"), index=False)
    with open(os.path.join(T, "table_error_analysis_correlations.md"), "w") as f:
        f.write(C.to_markdown(index=False, floatfmt=".4f"))
    pooled = g.groupby("dataset").gain.mean().sort_values()
    ext = pd.concat([pooled.head(8), pooled.tail(8)]).reset_index()
    ext.columns = ["dataset", "mean_gain_all_conditions"]
    with open(os.path.join(T, "table_error_analysis_extremes.md"), "w") as f:
        f.write(ext.to_markdown(index=False, floatfmt=".4f"))
    stats = dict(correlations=C.to_dict("records"), extremes=ext.to_dict("records"),
                 frac_datasets_gain_pos=float((pooled > 0).mean()), frac_datasets_gain_neg=float((pooled < 0).mean()))
    figures(g, P)
    stats["confusion"] = confusion(g)
    with open(os.path.join(S, "error_analysis.json"), "w") as f:
        json.dump(stats, f, indent=1, default=float)


def figures(g, P):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.4), sharey=True)
    for ax, mech in zip(axs, ["mcar", "block", "mnar"]):
        gg = g[g.mechanism == mech]
        for r, mk in zip(sorted(gg.test_rate.unique()), ["o", "s", "^"]):
            s = gg[gg.test_rate == r]
            ax.scatter(s.rel_gap_len, s.gain * 100, s=6, marker=mk, alpha=0.6, label=f"rate {r:.1f}")
        ax.axhline(0, color="grey", lw=0.7); ax.set_xscale("log")
        from matplotlib.ticker import NullFormatter
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_title(mech.upper() if mech != "block" else "Block"); ax.set_xlabel("mean gap length / series length")
    axs[0].set_ylabel("gain over MiniRocket+interp. (pp)"); axs[0].legend(fontsize=6)
    fig.tight_layout()
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_error_gain_vs_gap.{e}"), dpi=300)
    plt.close(fig)
    fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.0))
    for ax, c, lab in zip(axs, ["length", "n_train", "n_classes"], ["series length", "training-set size", "number of classes"]):
        ax.hist(P[c].astype(float), bins=20, color="0.5", edgecolor="black", lw=0.4)
        ax.set_xlabel(lab); ax.set_xscale("log" if c != "n_classes" else "linear")
    axs[0].set_ylabel("datasets")
    fig.tight_layout()
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_dataset_distribution.{e}"), dpi=300)
    plt.close(fig)


def confusion(g):
    from sklearn.metrics import confusion_matrix, recall_score
    from src.models.methods import run_method
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sub = g[(g.mechanism == "block") & (np.isclose(g.test_rate, 0.5))].sort_values("gain")
    out = {}
    cases = {"largest_loss": sub.iloc[0].dataset, "largest_gain": sub.iloc[-1].dataset}
    fig, axs = plt.subplots(2, 2, figsize=(7.1, 6.4))
    for row, (name, ds) in enumerate(cases.items()):
        Xtr, ytr, Xte, yte = corrupt(ds, "block", 0.5, 0.5, 0)
        res = {}
        for col, m in enumerate(["MissRocket", REF]):
            r = run_method(m, Xtr, ytr, Xte, 0)
            cm = confusion_matrix(yte, r["pred"], labels=np.unique(np.r_[ytr, yte]))
            res[m] = dict(accuracy=float((r["pred"] == yte).mean()),
                          per_class_recall=recall_score(yte, r["pred"], average=None, labels=np.unique(yte), zero_division=0).tolist())
            ax = axs[row, col]
            ax.imshow(cm, cmap="Greys")
            if cm.shape[0] <= 12:
                for i in range(cm.shape[0]):
                    for j in range(cm.shape[1]):
                        ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=6,
                                color="white" if cm[i, j] > cm.max() / 2 else "black")
            ax.set_title(f"{ds}: {'MissRocket' if m == 'MissRocket' else 'MiniRocket+interp.'} "
                         f"(acc {res[m]['accuracy']:.3f})", fontsize=7)
            ax.set_xlabel("predicted"); ax.set_ylabel("true")
        out[name] = dict(dataset=ds, **res)
    fig.tight_layout()
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_confusion_extremes.{e}"), dpi=300)
    plt.close(fig)
    return out


if __name__ == "__main__":
    main()
