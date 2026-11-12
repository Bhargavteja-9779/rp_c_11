# Review Round 1: Reviewer #1 (general, hostile but fair)

**Manuscript:** "Missing values in random-convolution time series classification: observed-tap weighting for MiniRocket and a pre-registered evaluation" (JKSU-CIS submission draft, build of 2026-11-12 ~11:35 UTC).

**Overall assessment:** The empirical work is extensive, and the paper is unusually candid about negative results. Several statements are nonetheless inaccurate or overstated relative to what was done, and parts of the package are incomplete. Recommendation at this stage: *major revision*.

## Issues

| # | Severity | Issue | Evidence | Required fix |
|---|---|---|---|---|
| 1 | **MAJOR** | "Pre-registered" in the title and abstract is misleading. The protocol was frozen in the authors' own version control, not registered with an independent registry (e.g. OSF). Reviewers and editors read "pre-registered" as public, time-stamped registration. | Title; abstract; Sect. 5.4 | Replace with "pre-specified" and describe exactly what was done: a frozen configuration committed before confirmatory runs, with the commit hash. |
| 2 | **MAJOR (correctness)** | Sect. 5.4 states "E1 used three seeds (0, 1 and 2)". After the infrastructure amendment the primary benchmark used **seed 0 only**; seeds 1–2 are restricted to a 30-dataset subset. The two protocol amendments (execution order; rescope after container reclamation) are not disclosed in the paper. | 05_setup.md vs PROGRESS.md items 13–14; config | Rewrite Sect. 5.4 to disclose both amendments, their timing (before inspecting any confirmatory accuracy) and their rationale. Correct the seed statement. |
| 3 | **MAJOR** | The method figures (pipeline, worked example) exist but are not included in the manuscript. A reader cannot see Proposition 3 in action. | Figures folder vs manuscript | Insert Fig. 1 (pipeline) in Sect. 4.2 and Fig. 2 (worked example) after Proposition 3, with accurate captions. |
| 4 | **MAJOR** | The Data availability statement promises "Online Resources" containing full statistics and raw results, but no supplementary files are assembled. | 09_declarations.md | Build Online Resource 1: full statistics tables, development log, the excluded/subset dataset lists and per-run results. |
| 5 | **MAJOR** | Seed variability is announced (Sect. 6.9, Discussion) but not yet reported. | Sect. 6.8 refers to 6.9 | Report the seed-variability analysis (E1 seeds 1–2 on the 30-dataset subset) once complete, together with the GRU-D UCR comparison (E2). |
| 6 | MODERATE | Multiplicity. Holm correction is applied within each condition. With nine conditions there is no family-wise control across conditions, and readers may over-interpret individual significant cells. | Sect. 5.5 | State explicitly that conditions are separate pre-specified hypotheses; that the pooled test is the overall test; and that per-condition p-values are descriptive of pattern. |
| 7 | MODERATE | "Gives an unbiased native estimator" in the abstract omits the qualifier: the estimator is unbiased only under MCAR, conditionally on the window being supported. | Abstract; Prop. 1(iii) | Qualify ("unbiased under random missingness"). |
| 8 | MODERATE | The block-gap length is fixed (mean 10% of the series length). Conclusions on "long gaps" depend on this choice, and gap-length sensitivity is examined only through natural variation across datasets. | Sect. 5.2, 6.8 | Acknowledge as a limitation; point to the error analysis showing the gain increases with realised gap length. |
| 9 | MODERATE | The stronger baselines (MultiRocket, Hydra-MultiRocket) are compared only with linear interpolation. A reader may ask whether they would benefit equally from weighting, which would change the practical conclusion. | Sect. 6.1, 7.2 | State clearly that weighting was not applied to them (method developed for PPV pooling of MiniRocket); list it as future work in Limitations (already partly there; make explicit). |
| 10 | MINOR | The excluded-dataset list in Sect. 5.1 is a placeholder-generated list; check that it renders. | Sect. 5.1 | Verify in build. |
| 11 | MINOR | Sect. 6 numbering skips the GRU-D UCR results; the forward references to "Section 6.9" must resolve. | Sect. 6.6, 6.8 | Add Sect. 6.9. |
| 12 | MINOR | Table 2 (main statistics) has wide numeric cells; the full CI/WTL version must be in the Online Resource as promised in the caption. | Table 2 caption | Include in Online Resource 1. |
| 13 | MINOR | The keyword "Robustness" is generic. | Keywords | Acceptable (4–6 keywords required); keep. |

## Not issues (checked)

- **Data leakage:** imputers are per-series or fit on training data only; biases and the ridge penalty are chosen on training data only; train/test masks are seeded independently. No leakage found.
- **Baseline fairness:** the reference aeon implementations are used with default settings. The LightGBM degenerate-default issue was fixed before the confirmatory runs. kNN imputation is included and wins where it should.
- **Citations:** all references were checked against Crossref, arXiv, PubMed or publisher pages (`supplementary/citation_audit_round1.csv`).

---

## Author response and changes (Round 1)

| # | Action taken |
|---|---|
| 1 | "Pre-registered" was replaced throughout (title, abstract, Sect. 1, 5.4, 8) by "pre-specified". Sect. 5.4 now states that the protocol was frozen in a version-controlled configuration (commit `6aca7cd`) before any confirmatory run. |
| 2 | Sect. 5.4 was rewritten to disclose amendment 1 (execution order) and amendment 2 (seed-0 primary analysis; seeds 1–2 and E3/E4 on a 30-dataset subset; E2 restriction), the infrastructure reason, and that both were made before any confirmatory accuracy was inspected. The erroneous "three seeds" statement was removed. |
| 3 | Fig. 1 (pipeline) and Fig. 2 (worked example, computed with the actual code on a development-set series) were inserted in Sect. 4.2. |
| 4 | Online Resource 1 (ESM_1.docx) is generated by `manuscript/build/build_supplement.py`. It contains the full per-condition statistics, the dataset lists, the development log and pointers to the raw CSVs; the raw results are provided as ESM_2.csv. |
| 5 | Sect. 6.9 was added after E1 seeds 1–2 and E2 completed (see review_02 onwards for verification). |
| 6 | A multiplicity paragraph was added to Sect. 5.5. |
| 7 | The abstract now reads "unbiased under random missingness". |
| 8 | A gap-length limitation was added to Sect. 7.4 (item 3). |
| 9 | Limitation 5 now explicitly states that weighting was not applied to MultiRocket and Hydra. |
| 10–12 | Verified in the rebuilt DOCX/PDF. |
