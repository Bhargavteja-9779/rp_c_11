"""Analysis of E9 (CWRU industrial case study, added after external review). Descriptive only: with four
leave-one-load-out folds no significance test is meaningful, so we report means, fold-level standard deviations
and the number of folds in which MissRocket beats each baseline.

Outputs (results/full/tables/): table_e9_summary.csv, table_e9_diff.csv, table_e9_recall.csv, table_e9_seed.csv,
figures/Fig_cwru.(png|pdf)
"""
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "results", "full", "E9_cwru", "raw_results.csv")
T = os.path.join(ROOT, "results", "full", "tables")
F = os.path.join(ROOT, "results", "full", "figures")
P = "MissRocket"
LABEL = {"MissRocket": "MissRocket (proposed)", "MissRocket-g0": "MissRocket w/o weighting (γ=0)",
         "AeonMiniRocket+linear": "MiniRocket + linear interp.", "AeonMiniRocket+knn": "MiniRocket + kNN impute",
         "HydraMultiRocket+linear": "Hydra-MultiRocket + linear interp.",
         "MaskRocket-noC": "Native masked MiniRocket (group-mean)", "LightGBM-NaN": "LightGBM (native NaN)"}
METHODS = list(LABEL)
COND = {"complete": ("Complete", "matched"), "random10": ("Random 10%", "matched"), "random30": ("Random 30%", "matched"),
        "random50": ("Random 50%", "matched"), "outage_short30": ("Short outages, 30%", "matched"),
        "outage_medium30": ("Medium outages, 30%", "matched"), "outage_long30": ("Long outages, 30%", "matched"),
        "outage_long50": ("Long outages, 50%", "matched"), "shift_random30": ("Random 30%", "shift"),
        "shift_outage_short30": ("Short outages, 30%", "shift"), "shift_outage_medium30": ("Medium outages, 30%", "shift"),
        "shift_outage_long30": ("Long outages, 30%", "shift"), "shift_outage_long50": ("Long outages, 50%", "shift")}
CLASSES = ["Normal", "IR007", "B007", "OR007@6", "IR014", "B014", "OR014@6", "IR021", "B021", "OR021@6"]
METRICS = ["accuracy", "macro_f1", "balanced_accuracy"]


def load():
    d = pd.read_csv(RAW)
    d = d[d.status == "ok"].drop_duplicates(["fold", "condition", "seed", "method"], keep="last")
    return d


def summary(d0):
    rows = []
    comp = d0[d0.condition == "complete"].set_index(["fold", "method"])
    for (c, m), g in d0.groupby(["condition", "method"]):
        r = dict(condition=c, scenario=COND[c][0], setting=COND[c][1], method=m, label=LABEL[m], n_folds=len(g))
        for k in METRICS:
            r[k] = g[k].mean(); r[k + "_sd"] = g[k].std(ddof=1)
            base = np.array([comp.loc[(f, m), k] for f in g.fold])
            r[k + "_drop"] = float(np.mean(base - g[k].values))  # degradation relative to complete data (same method, fold)
        r["fit_s"] = g.fit_s.mean(); r["predict_s"] = g.predict_s.mean()
        rows.append(r)
    s = pd.DataFrame(rows)
    s["order"] = s.condition.map(list(COND).index)
    return s.sort_values(["order", "method"]).drop(columns="order")


def diffs(d0):
    rows = []
    for c, g in d0.groupby("condition"):
        for k in METRICS:
            t = g.pivot(index="fold", columns="method", values=k)
            for b in METHODS[1:]:
                if b in t and P in t:
                    x = (t[P] - t[b]).dropna()
                    rows.append(dict(condition=c, scenario=COND[c][0], setting=COND[c][1], metric=k, baseline=b,
                                     label=LABEL[b], mean_diff=x.mean(), min_diff=x.min(), max_diff=x.max(),
                                     wins=int((x > 0).sum()), ties=int((x == 0).sum()), losses=int((x < 0).sum()), n=len(x)))
    return pd.DataFrame(rows)


def seed_check(d):
    """Seeds 0 and 1 for the three core methods: mean over (fold, seed) and per-seed MissRocket - baseline differences."""
    core = ["MissRocket", "MissRocket-g0", "AeonMiniRocket+linear"]
    rows = []
    for c, g in d[d.method.isin(core)].groupby("condition"):
        r = dict(condition=c, scenario=COND[c][0], setting=COND[c][1])
        for s in (0, 1):
            t = g[g.seed == s].pivot(index="fold", columns="method", values="accuracy")
            for b in core[1:]:
                r[f"diff_{b}_s{s}"] = (t[P] - t[b]).mean() if len(t) else np.nan
        for m in core:
            r[f"acc_{m}_2seeds"] = g[g.method == m].accuracy.mean()
        rows.append(r)
    return pd.DataFrame(rows)


def recall(d0):
    rows = []
    for (c, m), g in d0.groupby(["condition", "method"]):
        rc = np.mean([json.loads(v) for v in g.per_class_recall], axis=0)
        rows.append(dict(condition=c, method=m, label=LABEL[m], **{k: v for k, v in zip(CLASSES, rc)},
                         fault_mean=float(np.mean(rc[1:])), fault_min=float(np.min(rc[1:])), worst_fault=CLASSES[1 + int(np.argmin(rc[1:]))]))
    return pd.DataFrame(rows)


def figure(s):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    col = dict(zip(METHODS, ["#000000", "#000000", "#E69F00", "#56B4E9", "#009E73", "#D55E00", "#CC79A7"]))
    sty = dict(zip(METHODS, ["-", "--", "-", "-", "-", "-", "-"]))
    mk = dict(zip(METHODS, ["o", "o", "s", "h", "v", "P", "X"]))
    fig, axs = plt.subplots(1, 2, figsize=(7.1, 3.4), sharey=True, gridspec_kw=dict(width_ratios=[8, 5]))
    for ax, setting, title in zip(axs, ["matched", "shift"], ["(a) Same missingness in training and test data",
                                                             "(b) Trained on complete data, tested incomplete"]):
        conds = [c for c in COND if COND[c][1] == setting]
        if setting == "shift":
            conds = ["complete"] + conds
        x = np.arange(len(conds))
        for m in METHODS:
            y = [s[(s.condition == c) & (s.method == m)].accuracy.mean() for c in conds]
            ax.plot(x, y, marker=mk[m], color=col[m], ls=sty[m], lw=1.6 if m == P else 1.0, ms=4,
                    mfc="white" if m == "MissRocket-g0" else col[m], label=LABEL[m])
        ax.set_xticks(x)
        ax.set_xticklabels([COND[c][0].replace(", ", "\n") for c in conds], rotation=45, ha="right", fontsize=7)
        ax.set_title(title, fontsize=8.5); ax.grid(alpha=0.3)
    axs[0].set_ylabel("Accuracy (mean over 4 load folds)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_cwru.{ext}"), dpi=300)
    plt.close(fig)


def main():
    d = load()
    d0 = d[d.seed == 0]
    s = summary(d0); s.to_csv(os.path.join(T, "table_e9_summary.csv"), index=False)
    df = diffs(d0); df.to_csv(os.path.join(T, "table_e9_diff.csv"), index=False)
    seed_check(d).to_csv(os.path.join(T, "table_e9_seed.csv"), index=False)
    recall(d0).to_csv(os.path.join(T, "table_e9_recall.csv"), index=False)
    figure(s)
    piv = s.pivot(index="condition", columns="method", values="accuracy").reindex(list(COND))[METHODS]
    print(piv.round(3).to_string())
    print(df[df.metric == "accuracy"].pivot(index="condition", columns="baseline", values="wins").reindex(list(COND)).to_string())


if __name__ == "__main__":
    main()
