"""Generate all statistics, tables and figures from raw experiment outputs (no manual numbers).

Outputs (under results/<mode>/):
  statistics/statistics.json, metrics.json, raw_results.csv (all experiments concatenated)
  tables/*.csv and tables/*.md
  figures/*.png (300 dpi) and *.pdf
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from src.evaluation.io import read_results  # noqa: E402
from src.statistics.tests import compare, mean_ranks  # noqa: E402

PROPOSED = "MissRocket"
MAIN_BASELINES = ["AeonMiniRocket+linear", "AeonMiniRocket+zero", "AeonMiniRocket+mean", "AeonMiniRocket+locf",
                  "AeonMiniRocket+knn", "MultiRocket+linear", "HydraMultiRocket+linear", "MaskRocket-noC",
                  "LightGBM-NaN", "1NN-ED+linear"]
ABLATIONS = ["MissRocket-g0", "MissRocket-g0.5", "MissRocket-g2", "MissRocket+mask", "MissRocket-select",
             "MissRocket-zerofill", "MissRocket-g0-zerofill", "MissRocket-locf", "MissRocket-g0-locf",
             "MissRocket-knn", "MissRocket-g0-knn"]
LABEL = {"MissRocket": "MissRocket (proposed)", "AeonMiniRocket+linear": "MiniRocket + linear interp.",
         "AeonMiniRocket+zero": "MiniRocket + zero fill", "AeonMiniRocket+mean": "MiniRocket + mean fill",
         "AeonMiniRocket+locf": "MiniRocket + LOCF", "AeonMiniRocket+knn": "MiniRocket + kNN impute",
         "AeonMiniRocket+resample": "MiniRocket + resampling",
         "MultiRocket+linear": "MultiRocket + linear interp.", "HydraMultiRocket+linear": "Hydra-MultiRocket + linear interp.",
         "MaskRocket-noC": "Native masked MiniRocket (group-mean)", "LightGBM-NaN": "LightGBM (native NaN)",
         "1NN-ED+linear": "1-NN ED + linear interp.", "MissRocket-g0": "w/o weighting (γ=0)",
         "MissRocket-g0.5": "γ=0.5", "MissRocket-g2": "γ=2", "MissRocket+mask": "+ mask-pattern features",
         "MissRocket-select": "γ, mask selected by LOO", "MissRocket-zerofill": "zero gap filling, γ=1",
         "MissRocket-g0-zerofill": "zero gap filling, γ=0", "MissRocket-locf": "LOCF gap filling, γ=1",
         "MissRocket-g0-locf": "LOCF gap filling, γ=0",
         "MissRocket-knn": "kNN gap filling, γ=1", "MissRocket-g0-knn": "kNN gap filling, γ=0", "GRU-D": "GRU-D", "MissRocket-select-p12": "MissRocket-select"}


def md(df, path, floatfmt=".4f"):
    df.to_csv(path + ".csv", index=False)
    with open(path + ".md", "w") as f:
        f.write(df.to_markdown(index=False, floatfmt=floatfmt))


def seed_avg(d, metric="accuracy"):
    ok = d[d.status == "ok"]
    return ok.groupby(["dataset", "mechanism", "train_rate", "test_rate", "method"])[metric].mean().reset_index()


def ablation_tables(R, T, stats):
    if "E1" not in R or "E3" not in R:
        return
    e1 = R["E1"]
    e3 = R["E3"]
    keep_ds, keep_rates = set(e3.dataset), set(e3.test_rate)
    base = e1[(e1.seed == 0) & e1.method.isin([PROPOSED, "MissRocket-g0", "AeonMiniRocket+linear"])
              & e1.dataset.isin(keep_ds) & e1.test_rate.isin(keep_rates)]
    d = pd.concat([base, e3])
    a = seed_avg(d)
    stats["E3_n_datasets"] = int(len(keep_ds))
    rows, means = [], []
    for (mech, rate), g in a.groupby(["mechanism", "test_rate"]):
        tab = g.pivot(index="dataset", columns="method", values="accuracy").dropna()
        others = [m for m in ABLATIONS if m in tab] + (["AeonMiniRocket+linear"] if "AeonMiniRocket+linear" in tab else [])
        c = compare(tab, PROPOSED, others)
        c.insert(0, "rate", rate); c.insert(0, "mechanism", mech); rows.append(c)
        # paired effect of weighting under each gap filler
        for w, u, fill in [(PROPOSED, "MissRocket-g0", "linear"), ("MissRocket-zerofill", "MissRocket-g0-zerofill", "zero"),
                           ("MissRocket-locf", "MissRocket-g0-locf", "LOCF"), ("MissRocket-knn", "MissRocket-g0-knn", "kNN")]:
            if w in tab and u in tab:
                cc = compare(tab, w, [u]).iloc[0].to_dict()
                means.append(dict(mechanism=mech, rate=rate, gap_filler=fill, weighted_mean=tab[w].mean(),
                                  unweighted_mean=tab[u].mean(), **{k: cc[k] for k in ["mean_diff", "ci95_low", "ci95_high", "wins", "ties", "losses", "p_value"]}))
    ab = pd.concat(rows)
    ab["baseline"] = ab.baseline.map(lambda m: LABEL.get(m, m))
    md(ab.drop(columns="proposed"), os.path.join(T, "table_ablation_statistics"))
    stats["E3_ablation_comparisons"] = ab.to_dict("records")
    wf = pd.DataFrame(means)
    from src.statistics.tests import holm
    if len(wf):
        wf["p_holm"] = holm(wf.p_value.values)
        md(wf, os.path.join(T, "table_weighting_by_gap_filler"))
        stats["E3_weighting_by_filler"] = wf.to_dict("records")
    s = a.groupby(["mechanism", "method"]).accuracy.mean().unstack()
    s.columns = [LABEL.get(c, c) for c in s.columns]
    md(s.reset_index(), os.path.join(T, "table_ablation_means"))


def seed_variability(R, T, stats):
    """Amendment 2: seeds 1-2 exist only for the 30-dataset subset. Per seed, paired MissRocket - baseline
    differences over those datasets; agreement of the sign of the mean difference across seeds."""
    if "E1" not in R:
        return
    d = R["E1"][R["E1"].status == "ok"]
    multi = d.groupby("dataset").seed.nunique()
    ds = multi[multi > 1].index
    if len(ds) == 0:
        return
    sub = d[d.dataset.isin(ds)]
    rows = []
    for (mech, rate, seed), g in sub.groupby(["mechanism", "test_rate", "seed"]):
        tab = g.pivot_table(index="dataset", columns="method", values="accuracy")
        for b in MAIN_BASELINES + ["MissRocket-g0"]:
            if b in tab and PROPOSED in tab:
                dd = (tab[PROPOSED] - tab[b]).dropna()
                rows.append(dict(mechanism=mech, rate=rate, seed=seed, baseline=LABEL.get(b, b), n=len(dd),
                                 mean_diff=dd.mean(), wins=int((dd > 1e-9).sum()), losses=int((dd < -1e-9).sum())))
    t = pd.DataFrame(rows)
    piv = t.pivot_table(index=["mechanism", "rate", "baseline"], columns="seed", values="mean_diff").reset_index()
    piv.columns = [str(c) for c in piv.columns]
    sc = [c for c in piv.columns if c.isdigit()]
    piv["sd_over_seeds"] = piv[sc].std(axis=1)
    piv["sign_agreement"] = piv[sc].apply(lambda r: bool((r > 0).all() or (r < 0).all()), axis=1)
    md(piv, os.path.join(T, "table_seed_variability"))
    stats["E1_seed_variability"] = piv.to_dict("records")
    stats["E1_seed_variability_n_datasets"] = int(len(ds))


def main_tables(R, T, S, F, stats):
    if "E1" not in R:
        return
    d = R["E1"]
    d = d[d.seed == 0]  # amendment 2: primary analysis on seed 0 (all eligible datasets)
    stats["E1_errors"] = int((d.status != "ok").sum())
    a = seed_avg(d)
    a_bacc = seed_avg(d, "balanced_accuracy")
    a_f1 = seed_avg(d, "macro_f1")
    stats["E1_n_datasets"] = int(a.dataset.nunique())
    rows, comp_all, abl_all, rank_rows = [], [], [], []
    for (mech, rate), g in a.groupby(["mechanism", "test_rate"]):
        tab = g.pivot(index="dataset", columns="method", values="accuracy")
        methods = [m for m in [PROPOSED] + MAIN_BASELINES + ["MissRocket-g0"] if m in tab]
        tab = tab[methods].dropna()
        for m in methods:
            gb = a_bacc[(a_bacc.mechanism == mech) & (a_bacc.test_rate == rate) & (a_bacc.method == m)].balanced_accuracy
            gf = a_f1[(a_f1.mechanism == mech) & (a_f1.test_rate == rate) & (a_f1.method == m)].macro_f1
            rows.append(dict(mechanism=mech, rate=rate, method=LABEL.get(m, m), key=m, mean_accuracy=tab[m].mean(),
                             std_accuracy=tab[m].std(), mean_balanced_accuracy=gb.mean(), mean_macro_f1=gf.mean()))
        mains = [m for m in [PROPOSED] + MAIN_BASELINES if m in tab]
        rk = mean_ranks(tab[mains])
        for m, v in rk.items():
            rank_rows.append(dict(mechanism=mech, rate=rate, method=LABEL.get(m, m), key=m, mean_rank=v))
        c = compare(tab, PROPOSED, [m for m in MAIN_BASELINES if m in tab])
        c.insert(0, "rate", rate); c.insert(0, "mechanism", mech); comp_all.append(c)
        ab = compare(tab, PROPOSED, ["MissRocket-g0"]) if "MissRocket-g0" in tab else pd.DataFrame()
        if len(ab):
            ab.insert(0, "rate", rate); ab.insert(0, "mechanism", mech); abl_all.append(ab)
    summ = pd.DataFrame(rows)
    md(summ.drop(columns="key"), os.path.join(T, "table_main_accuracy"))
    comp = pd.concat(comp_all)
    comp["baseline"] = comp.baseline.map(lambda m: LABEL.get(m, m))
    md(comp.drop(columns="proposed"), os.path.join(T, "table_main_statistics"))
    abl = pd.concat(abl_all) if abl_all else pd.DataFrame(columns=["baseline", "proposed"])
    abl["baseline"] = abl.baseline.map(lambda m: LABEL.get(m, m))
    md(abl.drop(columns="proposed"), os.path.join(T, "table_weighting_vs_unweighted_3seeds"))
    rk = pd.DataFrame(rank_rows)
    md(rk.drop(columns="key"), os.path.join(T, "table_mean_ranks"))
    stats["E1_main_comparisons"] = comp.to_dict("records")
    stats["E1_ablation_comparisons"] = abl.to_dict("records")
    # pooled over all 9 conditions (dataset x condition units averaged per dataset)
    pooled = a.groupby(["dataset", "method"]).accuracy.mean().unstack()
    pc = compare(pooled, PROPOSED, [m for m in MAIN_BASELINES + ["MissRocket-g0"] if m in pooled])
    pc["baseline"] = pc.baseline.map(lambda m: LABEL.get(m, m))
    md(pc.drop(columns="proposed"), os.path.join(T, "table_pooled_statistics"))
    stats["E1_pooled_comparisons"] = pc.to_dict("records")
    # efficiency
    ok = d[d.status == "ok"].copy()
    ok["total_s"] = ok.fit_s + ok.predict_s
    eff = ok.groupby("method").agg(median_total_s=("total_s", "median"), mean_total_s=("total_s", "mean"),
                                   total_cpu_h=("total_s", lambda x: x.sum() / 3600), median_features=("n_features", "median")).reset_index()
    eff["method"] = eff.method.map(lambda m: LABEL.get(m, m))
    md(eff.sort_values("median_total_s"), os.path.join(T, "table_efficiency"), floatfmt=".3f")
    # selected gamma / mask
    mr = ok[ok.method == PROPOSED]
    if "selected_gamma" in mr:
        sel = mr.groupby(["mechanism", "test_rate", "selected_gamma"]).size().unstack(fill_value=0)
        sel = (sel.T / sel.sum(1)).T.reset_index()
        sel.columns = [str(c) for c in sel.columns]
        md(sel, os.path.join(T, "table_selected_gamma"), floatfmt=".3f")
        mk = mr.groupby(["mechanism", "test_rate"]).selected_mask.apply(lambda s: (s.astype(str) == "True").mean()).reset_index()
        md(mk, os.path.join(T, "table_selected_mask"), floatfmt=".3f")
    figures_main(a, summ, comp, F)


def figures_main(a, summ, comp, F):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    show = [PROPOSED, "AeonMiniRocket+linear", "MultiRocket+linear", "HydraMultiRocket+linear", "AeonMiniRocket+knn",
            "AeonMiniRocket+zero", "MaskRocket-noC", "LightGBM-NaN", "1NN-ED+linear"]
    mk = dict(zip(show, ["o", "s", "^", "v", "h", "D", "P", "X", "*"]))
    mechs = ["mcar", "block", "mnar"]
    fig, axs = plt.subplots(1, 3, figsize=(7.1, 3.3), sharey=True)
    for ax, mech in zip(axs, mechs):
        for m in show:
            s = summ[(summ.mechanism == mech) & (summ.key == m)].sort_values("rate")
            if len(s):
                ax.plot(s.rate, s.mean_accuracy, marker=mk[m], lw=1.6 if m == PROPOSED else 0.9,
                        color="black" if m == PROPOSED else None, label=LABEL.get(m, m), ms=4)
        ax.set_title({"mcar": "MCAR", "block": "Block (contiguous gaps)", "mnar": "MNAR (self-masking)"}[mech])
        ax.set_xlabel("Missing rate"); ax.grid(alpha=0.3)
    axs[0].set_ylabel("Mean accuracy over datasets")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=6.5, frameon=False)
    fig.tight_layout(rect=(0, 0.2, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_accuracy_vs_rate.{ext}"), dpi=300)
    plt.close(fig)
    # paired differences vs linear interpolation baseline
    fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.4), sharey=True)
    for ax, mech in zip(axs, mechs):
        data, labels = [], []
        for rate in sorted(a.test_rate.unique()):
            t = a[(a.mechanism == mech) & (a.test_rate == rate)].pivot(index="dataset", columns="method", values="accuracy")
            if PROPOSED in t and "AeonMiniRocket+linear" in t:
                data.append((t[PROPOSED] - t["AeonMiniRocket+linear"]).dropna().values * 100)
                labels.append(f"{rate:.1f}")
        ax.boxplot(data, tick_labels=labels, showfliers=True, flierprops=dict(ms=2))
        ax.axhline(0, color="grey", lw=0.8)
        ax.set_title(mech.upper() if mech != "block" else "Block")
        ax.set_xlabel("Missing rate")
    axs[0].set_ylabel("Accuracy difference (pp)\nMissRocket − MiniRocket+interp.")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_paired_differences.{ext}"), dpi=300)
    plt.close(fig)


def ablation_figure(R, F):
    if "E1" not in R or "E3" not in R:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    e1 = R["E1"]
    e3 = R["E3"]
    a = seed_avg(pd.concat([e1[(e1.seed == 0) & e1.method.isin([PROPOSED, "MissRocket-g0"]) & e1.dataset.isin(set(e3.dataset))
                               & e1.test_rate.isin(set(e3.test_rate))], e3]))
    ms = [PROPOSED, "MissRocket-g0", "MissRocket-g0.5", "MissRocket-g2", "MissRocket+mask", "MissRocket-select"]
    g = a[a.method.isin(ms)].groupby(["mechanism", "method"]).accuracy.mean().unstack()
    g = g[[m for m in ms if m in g]]
    fig, ax = plt.subplots(figsize=(7.1, 2.6))
    x = np.arange(len(g.index)); w = 0.8 / len(g.columns)
    for i, m in enumerate(g.columns):
        ax.bar(x + i * w, g[m].values, w, label=LABEL.get(m, m), hatch=["", "//", "..", "xx", "\\\\", "oo"][i % 6],
               edgecolor="black", lw=0.5)
    ax.set_xticks(x + w * (len(g.columns) - 1) / 2)
    ax.set_xticklabels([{"mcar": "MCAR", "block": "Block", "mnar": "MNAR"}[i] for i in g.index])
    lo = np.nanmin(g.values); ax.set_ylim(lo - 0.03, np.nanmax(g.values) + 0.02)
    ax.set_ylabel("Mean accuracy (all rates)")
    ax.legend(fontsize=6, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"Fig_ablation.{ext}"), dpi=300)
    plt.close(fig)


def shift_tables(R, T, stats):
    if "E4" not in R:
        return
    a = seed_avg(R["E4"])
    rows = []
    for (mech, tr, te), g in a.groupby(["mechanism", "train_rate", "test_rate"]):
        tab = g.pivot(index="dataset", columns="method", values="accuracy").dropna()
        c = compare(tab, PROPOSED, [m for m in tab.columns if m != PROPOSED])
        c.insert(0, "test_rate", te); c.insert(0, "train_rate", tr); c.insert(0, "mechanism", mech)
        c["proposed_mean"] = tab[PROPOSED].mean()
        c["baseline_mean"] = [tab[b].mean() for b in c.baseline]
        rows.append(c)
    s = pd.concat(rows)
    s["baseline"] = s.baseline.map(lambda m: LABEL.get(m, m))
    md(s.drop(columns="proposed"), os.path.join(T, "table_shift"))
    stats["E4_shift"] = s.to_dict("records")


def natural_tables(R, T, stats):
    if "E5_natural" not in R:
        return
    d = R["E5_natural"]
    a = d[d.status == "ok"].groupby(["dataset", "method"])[["accuracy", "balanced_accuracy"]].agg(["mean", "std"])
    a.columns = ["_".join(c) for c in a.columns]
    a = a.reset_index()
    wide = a.pivot(index="dataset", columns="method", values="accuracy_mean")
    wide.columns = [LABEL.get(c, c) for c in wide.columns]
    out = wide.reset_index()
    out.loc[len(out)] = ["MEAN"] + list(wide.mean().values)
    md(out, os.path.join(T, "table_natural"))
    tab = a.pivot(index="dataset", columns="method", values="accuracy_mean")
    c = compare(tab, PROPOSED, [m for m in tab.columns if m != PROPOSED])
    c["baseline"] = c.baseline.map(lambda m: LABEL.get(m, m))
    md(c.drop(columns="proposed"), os.path.join(T, "table_natural_statistics"))
    stats["E5_natural"] = c.to_dict("records")


def p12_tables(mode, T, F, stats):
    p = os.path.join(ROOT, "results", mode, "E5_p12", "raw_results.jsonl")
    if not os.path.exists(p):
        return
    recs = [json.loads(l) for l in open(p)]
    df = pd.DataFrame(recs)
    g = df.groupby("method").agg(auroc_mean=("auroc", "mean"), auroc_std=("auroc", "std"), auprc_mean=("auprc", "mean"),
                                 auprc_std=("auprc", "std"), time_s_mean=("time_s", "mean"), n_seeds=("seed", "count")).reset_index()
    g["method"] = g.method.map(lambda m: LABEL.get(m, m))
    md(g.sort_values("auroc_mean", ascending=False), os.path.join(T, "table_p12"))
    stats["E5_p12"] = df.drop(columns=["info"]).to_dict("records")
    stats["E5_p12_selection"] = [dict(seed=r["seed"], gamma=r["info"].get("gamma"), mask=r["info"].get("mask"))
                                 for r in recs if r["method"] == PROPOSED]
    # paired bootstrap of AUROC differences (seed-averaged scores, resampling patients)
    y = np.load(os.path.join(ROOT, "results", mode, "E5_p12", "y_test.npy"))
    from sklearn.metrics import roc_auc_score
    sc = {}
    for m in df.method.unique():
        ss = [np.load(os.path.join(ROOT, "results", mode, "E5_p12", f"scores_{m}_s{s}.npy")) for s in df[df.method == m].seed]
        z = [(s - s.mean()) / (s.std() + 1e-12) for s in ss]
        sc[m] = np.mean(z, axis=0)
    rng = np.random.RandomState(0)
    rows = []
    if PROPOSED in sc:
        B = 2000
        idx = [rng.randint(0, len(y), len(y)) for _ in range(B)]
        for m in sc:
            if m == PROPOSED:
                continue
            diffs = []
            for ii in idx:
                if y[ii].min() == y[ii].max():
                    continue
                diffs.append(roc_auc_score(y[ii], sc[PROPOSED][ii]) - roc_auc_score(y[ii], sc[m][ii]))
            diffs = np.array(diffs)
            point = roc_auc_score(y, sc[PROPOSED]) - roc_auc_score(y, sc[m])
            pval = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
            rows.append(dict(baseline=LABEL.get(m, m), auroc_diff_seed_ensemble=point, ci95_low=np.quantile(diffs, 0.025),
                             ci95_high=np.quantile(diffs, 0.975), bootstrap_p=min(1.0, pval), n_boot=len(diffs)))
        bt = pd.DataFrame(rows)
        md(bt, os.path.join(T, "table_p12_bootstrap"))
        stats["E5_p12_bootstrap"] = bt.to_dict("records")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sklearn.metrics import roc_curve, precision_recall_curve
        fig, axs = plt.subplots(1, 2, figsize=(7.1, 3.0))
        for m, s in sc.items():
            fpr, tpr, _ = roc_curve(y, s); pr, rc, _ = precision_recall_curve(y, s)
            lw = 1.8 if m == PROPOSED else 1.0
            axs[0].plot(fpr, tpr, lw=lw, label=f"{LABEL.get(m, m)} ({roc_auc_score(y, s):.3f})")
            axs[1].plot(rc, pr, lw=lw, label=LABEL.get(m, m))
        axs[0].plot([0, 1], [0, 1], "k:", lw=0.6)
        axs[0].set_xlabel("False positive rate"); axs[0].set_ylabel("True positive rate"); axs[0].legend(fontsize=6)
        axs[1].set_xlabel("Recall"); axs[1].set_ylabel("Precision")
        axs[1].axhline(y.mean(), color="grey", lw=0.6, ls=":")
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(os.path.join(F, f"Fig_p12_roc_pr.{ext}"), dpi=300)
        plt.close(fig)


def generic_table(R, key, T, stats, name):
    if key not in R:
        return
    d = R[key]
    a = seed_avg(d)
    g = a.groupby(["mechanism", "test_rate", "method"]).accuracy.agg(["mean", "std", "count"]).reset_index()
    md(g, os.path.join(T, f"table_{name}"))
    stats[key] = g.to_dict("records")
    if PROPOSED in a.method.unique():
        rows = []
        for (mech, rate), gg in a.groupby(["mechanism", "test_rate"]):
            tab = gg.pivot(index="dataset", columns="method", values="accuracy").dropna()
            c = compare(tab, PROPOSED, [m for m in tab.columns if m != PROPOSED])
            c.insert(0, "rate", rate); c.insert(0, "mechanism", mech); rows.append(c)
        if rows:
            c = pd.concat(rows)
            md(c.drop(columns="proposed"), os.path.join(T, f"table_{name}_statistics"))
            stats[key + "_statistics"] = c.to_dict("records")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    mode = ap.parse_args().mode
    base = os.path.join(ROOT, "results", mode)
    T, F, S = os.path.join(base, "tables"), os.path.join(base, "figures"), os.path.join(base, "statistics")
    for p in (T, F, S):
        os.makedirs(p, exist_ok=True)
    R = {}
    for key, sub in [("E1", "E1_main"), ("E3", "E3_ablation"), ("E2", "E2_deep"), ("E4", "E4_shift"), ("E5_natural", "E5_natural"),
                     ("E7", "E7_sensitivity")]:
        p = os.path.join(base, sub, "raw_results.csv")
        if os.path.exists(p):
            R[key] = read_results(p)
            R[key]["experiment"] = key
    if R:
        pd.concat(R.values()).to_csv(os.path.join(base, "raw_results.csv"), index=False)
    stats = {"mode": mode}
    main_tables(R, T, S, F, stats)
    seed_variability(R, T, stats)
    ablation_tables(R, T, stats)
    ablation_figure(R, F)
    shift_tables(R, T, stats)
    natural_tables(R, T, stats)
    p12_tables(mode, T, F, stats)
    generic_table(R, "E2", T, stats, "deep_baseline")
    generic_table(R, "E7", T, stats, "sensitivity")
    with open(os.path.join(S, "statistics.json"), "w") as f:
        json.dump(stats, f, indent=1, default=float)
    metrics = {}
    for k, d in R.items():
        ok = d[d.status == "ok"]
        metrics[k] = ok.groupby("method")[["accuracy", "balanced_accuracy", "macro_f1"]].mean().to_dict("index")
    with open(os.path.join(base, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=1, default=float)
    print("analysis written to", base)


if __name__ == "__main__":
    main()
