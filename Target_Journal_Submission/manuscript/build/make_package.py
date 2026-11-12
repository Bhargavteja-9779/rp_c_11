"""Assemble the top-level submission package layout from generated outputs (copies, never hand-edited).

Target_Journal_Submission/
  results/   raw_results.csv, metrics.json, statistics.json, error_analysis.json, experiment_logs/, per-experiment CSVs
  figures/   all generated figures (PNG 300 dpi + PDF)
  tables/    all generated tables (CSV + Markdown)
  supplementary/  Online Resources (ESM_1.docx, ESM_2.csv), citation audit, research design documents
"""
import glob
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", ".."))
CODE = os.path.join(PKG, "code")
RES = os.path.join(CODE, "results", "full")


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def main():
    out = os.path.join(PKG, "results")
    copy(os.path.join(RES, "raw_results.csv"), os.path.join(out, "raw_results.csv"))
    copy(os.path.join(RES, "metrics.json"), os.path.join(out, "metrics.json"))
    copy(os.path.join(RES, "statistics", "statistics.json"), os.path.join(out, "statistics.json"))
    if os.path.exists(os.path.join(RES, "statistics", "error_analysis.json")):
        copy(os.path.join(RES, "statistics", "error_analysis.json"), os.path.join(out, "error_analysis.json"))
    for f in glob.glob(os.path.join(RES, "*", "raw_results.*")):
        exp = os.path.basename(os.path.dirname(f))
        copy(f, os.path.join(out, "per_experiment", f"{exp}_{os.path.basename(f)}"))
    for f in glob.glob(os.path.join(CODE, "logs", "*.log")):
        copy(f, os.path.join(out, "experiment_logs", os.path.basename(f)))
    copy(os.path.join(CODE, "results", "dev", "dev_screening_v2.csv"), os.path.join(out, "development", "dev_screening_v2.csv"))
    copy(os.path.join(CODE, "results", "dev", "dev_viability_STALE.csv"), os.path.join(out, "development", "dev_viability_STALE_do_not_use.csv"))
    for f in glob.glob(os.path.join(RES, "figures", "*")):
        copy(f, os.path.join(PKG, "figures", os.path.basename(f)))
    for f in glob.glob(os.path.join(RES, "tables", "*")):
        copy(f, os.path.join(PKG, "tables", os.path.basename(f)))
    sup = os.path.join(PKG, "supplementary")
    for f in ["ESM_1.docx", "ESM_2.csv"]:
        p = os.path.join(PKG, "manuscript", f)
        if os.path.exists(p):
            copy(p, os.path.join(sup, f))
    print("package assembled in", PKG)


if __name__ == "__main__":
    main()
