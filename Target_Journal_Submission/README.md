# Target_Journal_Submission

Submission package for the *Journal of King Saud University – Computer and Information Sciences* (Springer Nature).

**Manuscript:** "Robust time-series classification under sensor dropouts: observed-tap-weighted MiniRocket and a pre-specified evaluation".

| Folder | Contents |
|---|---|
| `journal_selection/` | `selected_journal.md`, `journal_comparison.md`, `journal_verification.md`; measured submission-to-acceptance times (scripts + data) |
| `manuscript/` | `Final_Manuscript.docx` / `.pdf` (anonymised), `title_page.docx` / `.pdf`, `cover_letter.docx` / `.pdf`, `ESM_1.docx` (Online Resource 1), `ESM_2.csv` (Online Resource 2, raw results), `ESM_3.csv` (Online Resource 3, CWRU per-run results); `source/` (Markdown sources); `build/` (builders: verified bibliography, values, DOCX/PDF, supplement, package, consistency check) |
| `code/` | Complete implementation, `run_all.py`, tests, configuration, experiments, analysis (see `code/README.md`) |
| `results/` | `raw_results.csv` (all runs), `metrics.json`, `statistics.json`, `error_analysis.json`, `per_experiment/`, `experiment_logs/`, `development/` |
| `figures/`, `tables/` | All generated figures (PNG 300 dpi + PDF) and tables (CSV + Markdown) |
| `supplementary/` | Online Resources, citation audit, research-design documents (candidate directions, literature matrix, novelty map, hypotheses/experiments) |
| `REVIEW/` | `review_01.md` … `review_10.md` (ten adversarial review rounds with author responses), `response_to_external_review.md` (point-by-point response to the external review), `final_audit.md` (consistency, reproducibility, rejection-risk report, decision) |
| `dist/` | `JKSU-CIS_submission_upload.zip` (exactly the files to upload, with `UPLOAD_CHECKLIST.md`) and `Full_research_archive.zip` (everything except raw data) |

## Rebuild everything

Run each command separately:

```bash
cd code && python run_all.py --mode full
```

```bash
cd ../manuscript && python build/build_values.py && python build/build_manuscript.py
```

```bash
python build/build_values.py && python build/build_supplement.py && python build/build_frontmatter.py build/values.json
```

```bash
python build/consistency_check.py && python build/make_package.py && python build/make_zip.py
```

The development history, including negative results, issues found and protocol amendments, is in `../PROGRESS.md` and reproduced in Online Resource 1.
