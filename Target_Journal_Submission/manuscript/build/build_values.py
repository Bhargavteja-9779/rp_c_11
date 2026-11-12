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


def t(name):
    p = os.path.join(TAB, name + ".csv")
    return pd.read_csv(p) if os.path.exists(p) else None


def pfmt(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def md_table(df):
    cols = list(df.columns)
    out = "| " + " | ".join(cols) + " |\n|" + "|".join([":---"] + ["---:"] * (len(cols) - 1)) + "|\n"
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
            r[f"{MECH[mech]} {int(rate * 100)}%"] = f"{p.loc[meth, (mech, rate)]:.3f}"
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
    df.loc[df.Condition.duplicated(), "Condition"] = ""
    v["_tables"]["main_statistics"] = md_table(df)


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


def main():
    v = {"_tables": {}}
    conf = confirmatory_datasets()
    v["N_CONF"] = str(len(conf))
    v["EXCLUDED_LIST"] = ", ".join(excluded_confirmatory())
    v["N_EXCLUDED"] = str(len(excluded_confirmatory()))
    v["SUBSET30"] = ", ".join(subset30())
    table_main(v); table_stats(v); table_pooled(v); table_eff(v); table_natural(v); table_ablation(v)
    json.dump(v, open(os.path.join(HERE, "values.json"), "w"), indent=1, ensure_ascii=False)
    print("values:", [k for k in v if k != "_tables"], "tables:", list(v["_tables"]))


if __name__ == "__main__":
    main()
