# Final Audit, Rejection-Risk Report and Self-Decision (Phases 34, 35, 41, 42)

## Phase 34: Consistency audit

**Automated checks** (`manuscript/build/consistency_check.py`, output in `manuscript/build/consistency_check.md`), all **PASS** (0 failures):
- no unresolved placeholders or citation keys, and no PENDING markers;
- figures 1–7 and tables 1–11 numbered consecutively, each referenced in the text, and first cited in numerical order;
- every embedded figure file exists;
- equations (1)–(5) are numbered consecutively and each is referenced;
- the reference list is alphabetical, and every entry is cited;
- abstract length is 150–250 words; there are 4–6 keywords;
- the text contains no "revolutionary / unprecedented / perfect / guaranteed / state-of-the-art".

**Traceability.**
- Every number in the manuscript is inserted by `build_manuscript.py`, either from `values.json` (computed by `build_values.py` from result files) or from `{{Q:table;…}}` queries into generated CSV tables. No number was typed by hand.
- The Results, Discussion and Conclusion text was re-read in review round 10 against the tables, and 16 overstatements were corrected (see review_10.md).

**Chain checked: title ↔ abstract ↔ contributions ↔ method ↔ code ↔ experiments ↔ tables ↔ figures ↔ statistics ↔ conclusion.**
- *Title, abstract and conclusion* describe the same method (observed-tap-weighted PPV, γ=1, linear gap filling) and the same evidence, including the negative results.
- *Method and code:* Eq. (5) matches `_transform_hist`, Prop. 4 matches the unit tests, and the defaults match `MissRocket(fixed=(1.0, False), imputer="linear")` (review 4).
- *Experiments and tables:* E1/E2/E3/E4/E4b/E5/E7 → tables 1–11 and the Online Resource S-tables. The statistics come from `statistics.json`.

## Phase 35: Reproducibility audit (as a stranger)

| Question | Answer | Evidence |
|---|---|---|
| Can I install it? | Yes | `requirements.txt` with exact versions (Python 3.13.18), `environment.yml`, CPU-only PyTorch instructions |
| Can I obtain the data? | Yes | `scripts/download_data.sh` (UCR 2018 archive; PhysioNet 2012, open licence); `run_all.py` calls it automatically |
| Can I preprocess / train / evaluate? | Yes | A fresh `python run_all.py --mode quick` completed all 9 experiment stages and the analysis (exit 0; log `code/logs/quick_run_final.log`) |
| Do the unit tests pass? | Yes | 18/18 |
| Can I reproduce the reported metrics exactly? | Yes for the sample checked | 24/24 re-executed confirmatory runs equal the stored accuracies (`tables/table_reproducibility_check.csv`) |
| Can I regenerate tables and figures? | Yes | `run_all.py --mode full --skip-experiments` (analysis, figures, error analysis) |
| Can I regenerate the manuscript numbers? | Yes | `manuscript/build/build_values.py` then `build_manuscript.py` |
| Is the configuration understandable? | Yes | `config/experiments.yaml` (commented, including amendments) and README |
| Known non-determinism | Minor | Multithreaded floating-point reductions (BLAS, LightGBM, numba fastmath pooling) may change last-bit values. The sample re-run showed none. |

## Phase 41: Rejection-risk report

| # | Risk | Evidence | Severity | Mitigation | Fixed? |
|---|---|---|---|---|---|
| 1 | **Novelty**: method judged incremental | Weighted PPV is a small change; the masked-pooling idea is familiar | **High** | Framing on mechanism + cheap fix + extensive, honest evidence; explicit positioning vs masked pooling and partial convolution (Sect. 4.2) | Partly (inherent) |
| 2 | **Methodology**: γ fixed at 1, while 0.5 looks marginally better | Sensitivity (Sect. 6.7) | Low | Disclosed; γ chosen on the development set before the confirmatory runs | Yes (disclosed) |
| 3 | **Dataset**: the long-gap claim rests on simulation | No naturally long interior gaps in the benchmark | Medium | Mechanism shift, natural datasets and P12 reported; limitation 3 | Partly |
| 4 | **Statistics**: single-seed primary benchmark; per-condition multiplicity | Amendment 2 | Medium | Seed-variability analysis (signs of all significant effects stable, machine-checked); multiplicity paragraph; pooled test | Yes |
| 5 | **Reproducibility** | — | Low | Full code, data scripts, per-run results, exact re-run check | Yes |
| 6 | **Baselines**: not tuned; MultiRocket/Hydra without weighting; no Yao et al. | Sect. 5.3, limitations 5 and 7 | Medium | Equal treatment (no tuning for any method); strongest library baselines; kNN included and reported as winning where it wins | Partly |
| 7 | **Generalisation**: negative on PhysioNet 2012 | GRU-D and LightGBM significantly better | Medium | Reported in the abstract and discussion; scope stated (shape-based sensor-like series) | Disclosed |
| 8 | **Writing**: long paper (34 pp, 11 tables) | — | Low–Medium | Compact tables; full detail moved to Online Resource 1 | Partly |
| 9 | **Formatting** | Springer style followed: author–year references, Fig. captions, declarations after references | Low | Automated checks; separate title page | Yes |
| 10 | **Citations** | 45 entries verified; claims checked against primary sources; 3 incorrect paraphrases fixed | Low | citation_audit.md | Yes |
| 11 | **Journal scope** | ML / signal processing / pattern recognition in scope | Low | Cover letter states fit | Yes |
| 12 | **Journal-specific reviewer risk** | JKSU-CIS reviewers often expect a "new model beats SOTA" narrative; this paper reports mixed results | Medium | The honest framing is a strength for careful reviewers but may disappoint others; cannot be changed without misrepresenting results | No (by design) |
| 13 | **Publication integrity / compliance** | AI-agent use must be disclosed; protocol deviations | Low | AI use documented in Methods and Declarations; all deviations disclosed; no fabricated data or citations; author placeholders must be completed by humans | Yes (authors must complete placeholders) |
| 14 | **Timeline** | The journal's 66-day median does not guarantee this paper's decision time | Medium | Stated in journal_selection | n/a |

The overall rejection risk is **not zero**. The dominant risks are perceived incrementality (1) and reviewer expectations of uniformly positive results (12).

## Phase 42: Self-decision

**READY FOR SUBMISSION**, conditional on human authors completing the placeholders, which an AI agent must not fill in:
- author names, affiliations, ORCID and the corresponding-author e-mail (title page);
- the funding, competing-interests and author-contribution statements;
- confirmation and adaptation of the AI-use statement to the actual division of work;
- depositing the code repository, with the link added after acceptance;
- the submission date in the cover letter.

Justification: every pre-specified experiment, plus the post-hoc robustness and scaling experiments requested in review, has been executed. All claims are supported by machine-generated evidence, all identified errors were corrected, and the remaining weaknesses are disclosed limitations rather than defects requiring further experiments.
