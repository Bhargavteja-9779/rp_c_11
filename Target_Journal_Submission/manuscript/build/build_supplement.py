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
sys.path.insert(0, CODE)
from build_values import md_table, pfmt  # noqa: E402
from src.data.cwru import FILES as CWRU_FILES, CLASSES as CWRU_CLASSES  # noqa: E402
from common import REG, confirmatory_datasets, excluded_confirmatory, natural_datasets, subset30  # noqa: E402

HEAD = ("Online Resource 1 — Robust time-series classification under sensor dropouts: observed-tap-weighted MiniRocket "
        "and a pre-specified evaluation. Journal of King Saud University – Computer and Information Sciences. "
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
        if keep and l.startswith("## ") and "Negative" not in l and "Revision" not in l:
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
    for fig, cap in [("Fig_p12_roc_pr.png", "S11 PhysioNet 2012: ROC and precision-recall curves (test set c)"),
                     ("Fig_dataset_distribution.png", "S12 Distribution of series length, training-set size and number of classes over the confirmatory datasets"),
                     ("Fig_scaling.png", "S13 Controlled scaling benchmark: transform time vs series length")]:
        fp = os.path.join(RES, "figures", fig)
        if os.path.exists(fp):
            parts.append(f"## {cap}\n\n![]({fp}){{width=16cm}}")
    parts.append("## S14 Raw results\n\nAll per-run results are provided as Online Resource 2 (ESM_2.csv). Columns: dataset, mechanism, train_rate, "
                 "test_rate, seed, method, accuracy, balanced_accuracy, macro_f1, auroc, auprc, fit_s, predict_s, n_features, "
                 "train_obs_frac, test_obs_frac, selected_gamma, selected_mask, status, timestamp, experiment. "
                 "The per-run results of the CWRU case study (E9) are provided as Online Resource 3 (ESM_3.csv), with one row per "
                 "fold × scenario × seed × method and per-class recall in JSON format.")
    parts.append("## S15 Industrial case study (E9, CWRU): data, full results and per-class recall\n\n"
                 "Files (CWRU Bearing Data Center, https://engineering.case.edu/bearingdatacenter; loads 0, 1, 2, 3 hp in this order): "
                 + "; ".join(f"{c}: {', '.join(map(str, f))}" for c, f in CWRU_FILES.items())
                 + ". Normal-baseline files (97–100) are sampled at 48 kHz and were decimated to 12 kHz. "
                 "Seed 0; mean and standard deviation over the four leave-one-load-out folds; *_drop* = mean accuracy loss relative to "
                 "the same method on complete data.")
    e = t("table_e9_summary")
    if e is not None:
        parts.append(fmt(e[["scenario", "setting", "label", "accuracy", "accuracy_sd", "macro_f1", "balanced_accuracy", "accuracy_drop"]].rename(columns={"label": "method"}), 3))
        r = t("table_e9_recall")
        if r is not None:
            parts.append("**Per-class recall** (mean over folds, seed 0), for complete data and long outages at 30%:")
            r = r[r.condition.isin(["complete", "outage_long30", "shift_outage_long30"])]
            parts.append(fmt(r[["condition", "label"] + CWRU_CLASSES].rename(columns={"label": "method"}), 2))
        sd = t("table_e9_seed")
        if sd is not None:
            parts.append("**Seed check** (seeds 0 and 1; mean over folds of MissRocket − baseline accuracy):")
            parts.append(fmt(sd[["scenario", "setting"] + [c for c in sd.columns if c.startswith("diff_")]], 3))
    ed = t("table_edge")
    if ed is not None:
        parts.append("## S16 Single-thread inference cost on CWRU (edge-CPU proxy)\n\nOne CPU thread; fitted on fold 0, inference on "
                     "the test segments with long outages (30%). Latency: single-segment prediction including gap filling; peak RSS "
                     "includes the Python interpreter and libraries.")
        parts.append(fmt(ed, 2))
    md = os.path.join(HERE, "ESM_1.md")
    open(md, "w", encoding="utf-8").write("\n\n".join(parts))
    out = os.path.join(MS, "ESM_1.docx")
    subprocess.run(["pandoc", md, "-o", out], check=True)
    sys.path.insert(0, HERE)
    from build_manuscript import postprocess, to_pdf
    postprocess(out, out, size=9)
    shutil.copy(os.path.join(RES, "raw_results.csv"), os.path.join(MS, "ESM_2.csv"))
    if os.path.exists(os.path.join(RES, "E9_cwru", "raw_results.csv")):
        shutil.copy(os.path.join(RES, "E9_cwru", "raw_results.csv"), os.path.join(MS, "ESM_3.csv"))
    print("built", out, "and ESM_2.csv")


if __name__ == "__main__":
    main()
