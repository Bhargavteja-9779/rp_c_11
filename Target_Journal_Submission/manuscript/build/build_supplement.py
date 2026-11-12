"""Online Resources (Electronic Supplementary Material), generated from result files only.

ESM_1.docx: development log, dataset lists, full statistics (CIs, W/T/L, rank-biserial), secondary metrics,
            seed variability, GRU-D comparison, efficiency.
ESM_2.csv : all raw per-run results (one row per dataset x condition x seed x method).
"""
import json
import os
import shutil
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(MS, "..", ".."))
CODE = os.path.join(MS, "..", "code")
RES = os.path.join(CODE, "results", "full")
TAB = os.path.join(RES, "tables")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(CODE, "experiments"))
from build_values import md_table, pfmt  # noqa: E402
from common import REG, confirmatory_datasets, excluded_confirmatory, natural_datasets, subset30  # noqa: E402

HEAD = ("Online Resource 1 — Missing values in random-convolution time series classification: observed-tap weighting "
        "for MiniRocket and a pre-specified evaluation. Journal of King Saud University – Computer and Information Sciences. "
        "[Author names and affiliations withheld for double-anonymous review]")


def t(name):
    p = os.path.join(TAB, name + ".csv")
    return pd.read_csv(p) if os.path.exists(p) else None


def fmt(df, digits=4):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df[c] = [("" if pd.isna(x) else (pfmt(x) if c.startswith("p") else f"{x:.{digits}f}")) for x in df[c]]
    return md_table(df, first=2)


def dev_log():
    lines = open(os.path.join(ROOT, "PROGRESS.md"), encoding="utf-8").read().split("\n")
    out, keep = [], False
    for l in lines:
        if l.startswith("## Negative / iteration log"):
            keep = True
            continue
        if keep and l.startswith("## ") and "Negative" not in l:
            break
        if keep:
            out.append(l)
    return "\n".join(out)


def main():
    parts = [f"*{HEAD}*\n"]
    parts.append("## S1 Development log (design iterations, negative results, protocol issues)\n\n"
                 "Verbatim from the project's version-controlled progress log. Items refer to the development datasets unless stated otherwise.\n\n"
                 + dev_log())
    parts.append("## S2 Dataset lists\n")
    parts.append(f"**Eligible confirmatory datasets ({len(confirmatory_datasets())}):** " + ", ".join(confirmatory_datasets()))
    parts.append(f"**Confirmatory datasets excluded by the pre-specified compute rule ({len(excluded_confirmatory())}):** " + ", ".join(excluded_confirmatory()))
    parts.append("**Development datasets (10):** " + ", ".join(REG[REG.split == "development"].dataset))
    parts.append("**Natural (incomplete / variable-length) datasets (15):** " + ", ".join(natural_datasets()))
    parts.append("**30-dataset subset (seeds 1–2, E3, E4; random draw, seed 11):** " + ", ".join(subset30()))
    parts.append("## S3 Full per-condition statistics (E1, seed 0, accuracy)\n\nΔ = MissRocket − baseline (accuracy, proportion). "
                 "CI: percentile bootstrap over datasets (10,000 resamples). p_holm: Holm correction within condition over ten baselines.")
    c = t("table_main_statistics")
    parts.append(fmt(c[["mechanism", "rate", "baseline", "n_datasets", "mean_diff", "median_diff", "ci95_low", "ci95_high", "wins",
                        "ties", "losses", "rank_biserial", "p_value", "p_holm"]]))
    parts.append("## S4 Secondary metrics (E1, seed 0): mean balanced accuracy and macro-F1\n")
    m = t("table_main_accuracy")
    parts.append(fmt(m[["mechanism", "rate", "method", "mean_accuracy", "std_accuracy", "mean_balanced_accuracy", "mean_macro_f1"]]))
    for name, title in [("table_seed_variability", "S5 Seed variability (30-dataset subset, seeds 0–2): mean MissRocket − baseline difference per seed"),
                        ("table_deep_baseline", "S6 GRU-D on the restricted UCR subset (E2): mean accuracy"),
                        ("table_deep_baseline_statistics", "S7 GRU-D comparison statistics (E2)"),
                        ("table_efficiency", "S8 Efficiency of all methods (E1, seed 0)"),
                        ("table_selected_gamma", "S9 Choice of γ by the leave-one-out selection variant (E3)"),
                        ("table_sensitivity_summary", "S10 Sensitivity analysis (E7)")]:
        d = t(name)
        if d is not None:
            parts.append(f"## {title}\n")
            parts.append(fmt(d))
    parts.append("## S11 Raw results\n\nAll per-run results are provided as Online Resource 2 (ESM_2.csv). Columns: dataset, mechanism, train_rate, "
                 "test_rate, seed, method, accuracy, balanced_accuracy, macro_f1, auroc, auprc, fit_s, predict_s, n_features, "
                 "train_obs_frac, test_obs_frac, selected_gamma, selected_mask, status, timestamp, experiment.")
    md = os.path.join(HERE, "ESM_1.md")
    open(md, "w", encoding="utf-8").write("\n\n".join(parts))
    out = os.path.join(MS, "ESM_1.docx")
    subprocess.run(["pandoc", md, "-o", out], check=True)
    sys.path.insert(0, HERE)
    from build_manuscript import postprocess, to_pdf
    postprocess(out, out, size=9)
    shutil.copy(os.path.join(RES, "raw_results.csv"), os.path.join(MS, "ESM_2.csv"))
    print("built", out, "and ESM_2.csv")


if __name__ == "__main__":
    main()
