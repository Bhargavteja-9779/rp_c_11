"""Create build/values.json: scalar values and formatted manuscript tables, computed ONLY from
machine-generated result files (code/results/full) and the dataset registry. No number is typed by hand."""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, "..", "..", "code"))
RES = os.path.join(CODE, "results", "full")
TAB = os.path.join(RES, "tables")
sys.path.insert(0, os.path.join(CODE, "experiments"))
sys.path.insert(0, CODE)
from common import confirmatory_datasets, excluded_confirmatory, subset30  # noqa: E402

COND = [("mcar", 0.2), ("mcar", 0.5), ("mcar", 0.8), ("block", 0.2), ("block", 0.5), ("block", 0.8),
        ("mnar", 0.2), ("mnar", 0.5), ("mnar", 0.8)]
MECH = {"mcar": "MCAR", "block": "Block", "mnar": "MNAR"}
CODE_ = {"mcar": "C", "block": "B", "mnar": "N"}


def ccode(mech, rate):
    return f"{CODE_[mech]}{int(rate * 100)}"


def t(name):
    p = os.path.join(TAB, name + ".csv")
    return pd.read_csv(p) if os.path.exists(p) else None


def pfmt(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def md_table(df, first=3):
    """Pipe table; dash counts set relative column widths in pandoc (first column `first` times wider)."""
    cols = list(df.columns)
    seps = [":" + "-" * (10 * first)] + ["-" * 10 + ":"] * (len(cols) - 1)
    out = "| " + " | ".join(cols) + " |\n|" + "|".join(seps) + "|\n"
    for _, r in df.iterrows():
        out += "| " + " | ".join(str(r[c]) for c in cols) + " |\n"
    return out


def table_main(v):
    m = t("table_main_accuracy")
    rk = t("table_mean_ranks")
    p = m.pivot_table(index="method", columns=["mechanism", "rate"], values="mean_accuracy")
    rows = []
    for meth in p.index:
        r = {"Method": meth}
        for mech, rate in COND:
            r[ccode(mech, rate)] = f"{p.loc[meth, (mech, rate)]:.3f}"
        r["Mean"] = f"{np.mean([p.loc[meth, c] for c in COND]):.3f}"
        rr = rk[rk.method == meth].mean_rank
        r["Mean rank"] = f"{rr.mean():.2f}" if len(rr) else "–"
        rows.append(r)
    df = pd.DataFrame(rows)
    df = df.assign(_m=df.Mean.astype(float)).sort_values("_m", ascending=False).drop(columns="_m")
    # bold best per column
    for c in df.columns[1:-1]:
        best = df[c].astype(float).max()
        df[c] = [f"**{x}**" if float(x) == best else x for x in df[c]]
    v["_tables"]["main_accuracy"] = md_table(df)


def table_stats(v):
    c = t("table_main_statistics")
    base = ["MiniRocket + linear interp.", "MultiRocket + linear interp.", "Hydra-MultiRocket + linear interp.",
            "MiniRocket + kNN impute"]
    g0 = t("table_weighting_vs_unweighted_3seeds")
    rows = []
    for mech, rate in COND:
        for b in base:
            r = c[(c.mechanism == mech) & (np.isclose(c.rate, rate)) & (c.baseline == b)].iloc[0]
            rows.append(dict(Condition=f"{MECH[mech]} {int(rate * 100)}%", Baseline=b,
                             **{"Δ acc. (pp) [95% CI]": f"{r.mean_diff * 100:+.2f} [{r.ci95_low * 100:+.2f}, {r.ci95_high * 100:+.2f}]",
                                "W/T/L": f"{r.wins}/{r.ties}/{r.losses}", "r_rb": f"{r.rank_biserial:+.2f}",
                                "p (Holm)": pfmt(r.p_holm)}))
        r = g0[(g0.mechanism == mech) & (np.isclose(g0.rate, rate))].iloc[0]
        rows.append(dict(Condition=f"{MECH[mech]} {int(rate * 100)}%", Baseline="w/o weighting (γ=0)",
                         **{"Δ acc. (pp) [95% CI]": f"{r.mean_diff * 100:+.2f} [{r.ci95_low * 100:+.2f}, {r.ci95_high * 100:+.2f}]",
                            "W/T/L": f"{r.wins}/{r.ties}/{r.losses}", "r_rb": f"{r.rank_biserial:+.2f}",
                            "p (Holm)": pfmt(r.p_holm)}))
    df = pd.DataFrame(rows)
    full = df.copy()
    full.loc[full.Condition.duplicated(), "Condition"] = ""
    v["_tables"]["main_statistics_full"] = md_table(full, first=1)
    df["cell"] = [f"{d.split(' [')[0]} ({p})" for d, p in zip(df["Δ acc. (pp) [95% CI]"], df["p (Holm)"])]
    piv = df.pivot(index="Baseline", columns="Condition", values="cell")
    piv = piv[[f"{MECH[m]} {int(r * 100)}%" for m, r in COND]]
    piv.columns = [ccode(m, r) for m, r in COND]
    order = ["MiniRocket + linear interp.", "w/o weighting (γ=0)", "MultiRocket + linear interp.",
             "Hydra-MultiRocket + linear interp.", "MiniRocket + kNN impute"]
    piv = piv.loc[order].reset_index().rename(columns={"Baseline": "MissRocket vs."})
    v["_tables"]["main_statistics"] = md_table(piv, first=2)


def table_pooled(v):
    c = t("table_pooled_statistics")
    df = pd.DataFrame(dict(Baseline=c.baseline,
                           **{"Δ acc. (pp) [95% CI]": [f"{a * 100:+.2f} [{b * 100:+.2f}, {d * 100:+.2f}]" for a, b, d in zip(c.mean_diff, c.ci95_low, c.ci95_high)],
                              "W/T/L": [f"{a}/{b}/{d}" for a, b, d in zip(c.wins, c.ties, c.losses)],
                              "r_rb": [f"{x:+.2f}" for x in c.rank_biserial], "p (Holm)": [pfmt(x) for x in c.p_holm]}))
    v["_tables"]["pooled"] = md_table(df)


def table_eff(v):
    e = t("table_efficiency")
    if e is None:
        return
    keep = ["MissRocket (proposed)", "w/o weighting (γ=0)", "MiniRocket + linear interp.", "MiniRocket + kNN impute",
            "MultiRocket + linear interp.", "Hydra-MultiRocket + linear interp.", "Native masked MiniRocket (group-mean)",
            "LightGBM (native NaN)", "1-NN ED + linear interp."]
    e = e[e.method.isin(keep)].copy()
    ref = float(e[e.method == "MiniRocket + linear interp."].median_total_s.iloc[0])
    df = pd.DataFrame(dict(Method=e.method, **{"Median time per run (s)": [f"{x:.2f}" for x in e.median_total_s],
                                                "Relative to MiniRocket+interp.": [f"{x / ref:.1f}×" for x in e.median_total_s],
                                                "Total wall time, 9 conditions (h)": [f"{x:.2f}" for x in e.total_cpu_h],
                                                "Features": [f"{int(x):,}" for x in e.median_features]}))
    v["_tables"]["efficiency"] = md_table(df)
    mr = float(e[e.method == "MissRocket (proposed)"].median_total_s.iloc[0])
    hy = float(e[e.method == "Hydra-MultiRocket + linear interp."].median_total_s.iloc[0])
    v["TIME_RATIO_MR_VS_MINI"] = f"{mr / ref:.1f}"
    v["TIME_RATIO_HYDRA_VS_MR"] = f"{hy / mr:.1f}"


def table_natural(v):
    n = t("table_natural")
    if n is None:
        return
    order = ["dataset", "MissRocket (proposed)", "w/o weighting (γ=0)", "MiniRocket + linear interp.", "MiniRocket + resampling",
             "Native masked MiniRocket (group-mean)", "LightGBM (native NaN)", "1-NN ED + linear interp."]
    n = n[order].rename(columns={"dataset": "Dataset"})
    for c in order[1:]:
        n[c] = [f"{x:.3f}" for x in n[c]]
    for i, r in n.iterrows():
        vals = [float(r[c]) for c in order[1:]]
        best = max(vals)
        for c in order[1:]:
            if float(r[c]) == best:
                n.at[i, c] = f"**{r[c]}**"
    n["Dataset"] = n["Dataset"].replace({"MEAN": "Mean"})
    v["_tables"]["natural"] = md_table(n)


def table_ablation(v):
    c = t("table_ablation_statistics")
    m = t("table_ablation_means")
    if c is None:
        return
    order = ["w/o weighting (γ=0)", "γ=0.5", "γ=2", "+ mask-pattern features", "γ, mask selected by LOO",
             "LOCF gap filling, γ=1", "zero gap filling, γ=1", "kNN gap filling, γ=1"]
    rows = []
    for b in order:
        r = {"Variant (vs. MissRocket)": b}
        for mech in ["mcar", "block", "mnar"]:
            x = c[(c.mechanism == mech) & (c.baseline == b)].iloc[0]
            acc = float(m[m.mechanism == mech][b].iloc[0])
            r[f"{MECH[mech]}: acc."] = f"{acc:.3f}"
            r[f"{MECH[mech]}: Δ (pp), p"] = f"{x.mean_diff * 100:+.2f}, {pfmt(x.p_holm)}"
        rows.append(r)
    top = {"Variant (vs. MissRocket)": "MissRocket (γ=1, linear filling)"}
    for mech in ["mcar", "block", "mnar"]:
        top[f"{MECH[mech]}: acc."] = f"{float(m[m.mechanism == mech]['MissRocket (proposed)'].iloc[0]):.3f}"
        top[f"{MECH[mech]}: Δ (pp), p"] = "–"
    v["_tables"]["ablation"] = md_table(pd.DataFrame([top] + rows))
    w = t("table_weighting_by_gap_filler")
    w = w[np.isclose(w.rate, 0.5)]
    rows = []
    for fill in ["linear", "LOCF", "zero", "kNN"]:
        r = {"Gap filler": fill}
        for mech in ["mcar", "block", "mnar"]:
            x = w[(w.mechanism == mech) & (w.gap_filler == fill)].iloc[0]
            r[MECH[mech]] = f"{x.mean_diff * 100:+.2f} ({x.wins}/{x.ties}/{x.losses}; p {pfmt(x.p_holm)})"
        rows.append(r)
    v["_tables"]["weighting_by_filler"] = md_table(pd.DataFrame(rows))


def table_shift(v):
    c = t("table_shift")
    if c is None:
        return
    rows = []
    for (mech, tr, te), g in c.groupby(["mechanism", "train_rate", "test_rate"], sort=False):
        r = {"Mechanism": MECH[mech], "Train → test rate": f"{int(tr * 100)}% → {int(te * 100)}%",
             "MissRocket": f"{g.proposed_mean.iloc[0]:.3f}"}
        for b, lab in [("MiniRocket + linear interp.", "MiniRocket + interp."), ("Native masked MiniRocket (group-mean)", "Native masked"),
                       ("LightGBM (native NaN)", "LightGBM")]:
            x = g[g.baseline == b].iloc[0]
            r[lab] = f"{x.baseline_mean:.3f} ({x.mean_diff * 100:+.1f}; {x.wins}/{x.ties}/{x.losses}; p {pfmt(x.p_holm)})"
        rows.append(r)
    v["_tables"]["shift"] = md_table(pd.DataFrame(rows))


def table_p12(v):
    p = t("table_p12")
    if p is None:
        return
    df = pd.DataFrame(dict(Method=p.method, AUROC=[f"{x:.3f}" for x in p.auroc_mean], AUPRC=[f"{x:.3f}" for x in p.auprc_mean],
                           **{"Time (s)": [f"{x:.0f}" for x in p.time_s_mean]}))
    v["_tables"]["p12"] = md_table(df)
    b = t("table_p12_bootstrap")
    if b is not None:
        v["_tables"]["p12boot"] = md_table(pd.DataFrame(dict(Method=b.baseline, **{
            "ΔAUROC (MissRocket − method)": [f"{x:+.3f}" for x in b.auroc_diff_seed_ensemble],
            "95% CI": [f"[{a:+.3f}, {c:+.3f}]" for a, c in zip(b.ci95_low, b.ci95_high)],
            "Bootstrap p": [pfmt(x) for x in b.bootstrap_p]})))
    g = p[p.method == "GRU-D"]
    if False:
        mr = float(p[p.method == "MissRocket (proposed)"].auroc_mean.iloc[0])
        gv = float(g.auroc_mean.iloc[0])
        v["P12_GRUD_SENTENCE"] = (f"GRU-D obtained AUROC {gv:.3f} ("
                                  + ("higher" if gv > mr else "lower") + f" than MissRocket's {mr:.3f}), at a training time of "
                                  f"{float(g.time_s_mean.iloc[0]):.0f} s on CPU.")
    else:
        v["P12_GRUD_SENTENCE"] = "GRU-D did not complete (see Limitations)."


def error_values(v):
    p = os.path.join(RES, "statistics", "error_analysis.json")
    if not os.path.exists(p):
        return
    e = json.load(open(p))
    v["ERR_FRAC_POS"] = f"{100 * e['frac_datasets_gain_pos']:.0f}"
    v["ERR_FRAC_NEG"] = f"{100 * e['frac_datasets_gain_neg']:.0f}"
    ex = sorted(e["extremes"], key=lambda r: r["mean_gain_all_conditions"])
    v["ERR_WORST"] = ", ".join(f"{r['dataset']} ({100 * r['mean_gain_all_conditions']:+.1f} pp)" for r in ex[:3])
    v["ERR_BEST"] = ", ".join(f"{r['dataset']} ({100 * r['mean_gain_all_conditions']:+.1f} pp)" for r in ex[::-1][:3])
    c = e["confusion"]
    v["CM_LOSS_DS"] = c["largest_loss"]["dataset"]; v["CM_GAIN_DS"] = c["largest_gain"]["dataset"]
    v["CM_LOSS_MR"] = f"{c['largest_loss']['MissRocket']['accuracy']:.3f}"; v["CM_LOSS_REF"] = f"{c['largest_loss']['AeonMiniRocket+linear']['accuracy']:.3f}"
    v["CM_GAIN_MR"] = f"{c['largest_gain']['MissRocket']['accuracy']:.3f}"; v["CM_GAIN_REF"] = f"{c['largest_gain']['AeonMiniRocket+linear']['accuracy']:.3f}"
    g = pd.read_csv(os.path.join(TAB, "table_error_analysis_per_dataset.csv"))
    worst = g.sort_values("gain").head(6)
    v["ERR_WORST_CASES"] = "; ".join(f"{r.dataset} ({MECH[r.mechanism]} {int(r.test_rate * 100)}%, {100 * r.gain:+.1f} pp)" for r in worst.itertuples())
    reg = pd.read_csv(os.path.join(CODE, "data", "registry.csv")).set_index("dataset")
    v["ERR_WORST_NTEST"] = ", ".join(f"{d}: {int(reg.loc[d, 'n_test'])}" for d in dict.fromkeys(worst.dataset))


def e2_values(v):
    p = os.path.join(RES, "E2_deep", "raw_results.csv")
    if not os.path.exists(p):
        return
    sys.path.insert(0, CODE)
    from src.evaluation.io import read_results
    d = read_results(p)
    d = d[d.status == "ok"]
    med = (d.fit_s + d.predict_s).groupby(d.method).median()
    v["GRUD_MED_S"] = f"{med['GRU-D']:.1f}"
    v["MR_MED_S_E2"] = f"{med['MissRocket']:.2f}"
    v["GRUD_TIME_RATIO"] = f"{med['GRU-D'] / med['MissRocket']:.0f}"


def table_mechshift(v):
    g = t("table_mechanism_shift"); c = t("table_mechanism_shift_statistics")
    if g is None or c is None:
        return
    lab = {"MissRocket": "MissRocket", "MissRocket-g0": "w/o weighting (γ=0)", "AeonMiniRocket+linear": "MiniRocket + linear interp.",
           "AeonMiniRocket+knn": "MiniRocket + kNN impute", "MaskRocket-noC": "Native masked MiniRocket", "LightGBM-NaN": "LightGBM (native NaN)"}
    rows = []
    for m in lab:
        r = {"Method": lab[m]}
        for mech, name in [("mcar>block", "Train MCAR → test block"), ("block>mcar", "Train block → test MCAR")]:
            acc = float(g[(g.mechanism == mech) & (g.method == m)]["mean"].iloc[0])
            if m == "MissRocket":
                r[name] = f"{acc:.3f}"
            else:
                x = c[(c.mechanism == mech) & (c.baseline == m)].iloc[0]
                r[name] = f"{acc:.3f} ({x.mean_diff * 100:+.1f}; {x.wins}/{x.ties}/{x.losses}; p {pfmt(x.p_holm)})"
        rows.append(r)
    v["_tables"]["mechshift"] = md_table(pd.DataFrame(rows), first=2)


def main():
    v = {"_tables": {}}
    conf = confirmatory_datasets()
    v["N_CONF"] = str(len(conf))
    v["EXCLUDED_LIST"] = ", ".join(excluded_confirmatory())
    v["N_EXCLUDED"] = str(len(excluded_confirmatory()))
    v["SUBSET30"] = ", ".join(subset30())
    table_main(v); table_stats(v); table_pooled(v); table_eff(v); table_natural(v); table_ablation(v); table_shift(v); table_p12(v); error_values(v); e2_values(v); table_mechshift(v)
    json.dump(v, open(os.path.join(HERE, "values.json"), "w"), indent=1, ensure_ascii=False)
    print("values:", [k for k in v if k != "_tables"], "tables:", list(v["_tables"]))


if __name__ == "__main__":
    main()
