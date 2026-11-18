"""Build the final ZIP archives (copies of generated outputs only).

1. JKSU-CIS_submission_upload.zip — exactly the files to upload in the journal's submission system:
     01_Manuscript_anonymised.docx (+ .pdf for checking), 02_Title_page.docx, 03_Cover_letter.docx,
     Figures/Fig1..FigN (PNG 300 dpi, numbered in order of first citation), ESM_1.docx, ESM_2.csv, ESM_3.csv,
     UPLOAD_CHECKLIST.md
2. Full_research_archive.zip — the complete Target_Journal_Submission folder (code without raw data,
   results, review history), kept by the authors; the code is shared on reasonable request.
"""
import os
import re
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.abspath(os.path.join(HERE, ".."))
PKG = os.path.abspath(os.path.join(MS, ".."))
FIG = os.path.join(PKG, "code", "results", "full", "figures")
OUT = os.path.join(PKG, "dist")

CHECKLIST = """# Upload checklist — Journal of King Saud University – Computer and Information Sciences (Springer Nature)

Submission system: Springer Nature submission portal (via the journal's "Submit manuscript" link).
Article type: Original Article (research article). Review model: double-anonymous.

| Upload slot | File |
|---|---|
| Manuscript (anonymised, no author names) | 01_Manuscript_anonymised.docx |
| Title page (author details, declarations) | 02_Title_page.docx |
| Cover letter | 03_Cover_letter.docx |
| Figures (separate files, 300 dpi) | Figures/Fig*.png |
| Supplementary material (Online Resources 1–3) | ESM_1.docx, ESM_2.csv, ESM_3.csv |

Before uploading, the authors must complete the bracketed placeholders, which appear ONLY in the title page and cover letter:
- second author's full name, department, institution, city and country (corresponding author);
- corresponding author's e-mail address and both authors' ORCID iDs;
- first author's department, institution, city and country;
- the date of the cover letter.

The manuscript itself contains no placeholders and no author-identifying information.
01_Manuscript_anonymised.pdf is included only so that the layout can be checked; upload the DOCX.
Data and code statements: data are public (links in the Statements and Declarations); code is available on reasonable request.
"""


def figure_order():
    md = open(os.path.join(HERE, "Final_Manuscript_combined.md"), encoding="utf-8").read()
    return [os.path.basename(p) for p in dict.fromkeys(re.findall(r"!\[[^\]]*\]\(([^)]+\.png)\)", md))]


def upload_zip():
    d = os.path.join(OUT, "JKSU-CIS_submission_upload")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "Figures"))
    for src, dst in [("Final_Manuscript.docx", "01_Manuscript_anonymised.docx"), ("Final_Manuscript.pdf", "01_Manuscript_anonymised.pdf"),
                     ("title_page.docx", "02_Title_page.docx"), ("cover_letter.docx", "03_Cover_letter.docx"),
                     ("ESM_1.docx", "ESM_1.docx"), ("ESM_2.csv", "ESM_2.csv"), ("ESM_3.csv", "ESM_3.csv")]:
        shutil.copy2(os.path.join(MS, src), os.path.join(d, dst))
    for i, f in enumerate(figure_order(), 1):
        shutil.copy2(os.path.join(FIG, f), os.path.join(d, "Figures", f"Fig{i}_{f.replace('Fig_', '').replace('Fig1_', '').replace('Fig2_', '')}"))
    open(os.path.join(d, "UPLOAD_CHECKLIST.md"), "w").write(CHECKLIST)
    z = d + ".zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(d):
            for f in sorted(files):
                p = os.path.join(root, f)
                zf.write(p, os.path.relpath(p, OUT))
    return z


def archive_zip():
    z = os.path.join(OUT, "Full_research_archive.zip")
    skip = ("/dist", "/code/data/raw", "/code/data/cache", "__pycache__", "/.pytest_cache", "/code/.venv")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PKG):
            rel = "/" + os.path.relpath(root, PKG)
            if any(s in rel + "/" for s in skip):
                continue
            for f in sorted(files):
                p = os.path.join(root, f)
                zf.write(p, os.path.join("Target_Journal_Submission", os.path.relpath(p, PKG)))
        prog = os.path.join(PKG, "..", "PROGRESS.md")
        if os.path.exists(prog):
            zf.write(prog, "Target_Journal_Submission/PROGRESS.md")
    return z


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for z in (upload_zip(), archive_zip()):
        print(z, f"{os.path.getsize(z) / 2**20:.1f} MB")
