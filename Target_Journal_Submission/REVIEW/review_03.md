# Review Round 3: Reviewer #3 (statistical validity, experimental fairness, seeds, splitting, leakage)

## Issues

| # | Severity | Issue | Required fix / response |
|---|---|---|---|
| 1 | **MAJOR (statistical error)** | *Pseudo-replication in the error analysis.* Spearman correlations between per-dataset gain and dataset properties were computed on 273 points per mechanism, pooling the three rates. Each dataset appears three times and the points are not independent. Both the gain and the realised gap length increase with the rate, so pooling manufactures a cross-dataset correlation. | **Fixed.** Correlations are now computed within each (mechanism, rate), with n = 91 datasets and Holm correction within mechanism (`scripts/error_analysis.py`). The result changes the conclusion: only at block 80% are associations significant (series length ρ=0.35; absolute gap length ρ=0.34; relative gap length ρ=−0.36). Under MNAR, none is significant. Sect. 6.8 and the Discussion (7.1, limitation 3) were rewritten. The claim "the gain grows with the realised gap length" was removed. Evidence for the long-gap mechanism now rests on the mechanism × rate pattern of the confirmatory tests. |
| 2 | MAJOR | *Single seed in the primary benchmark.* Seed variance could alter individual-dataset differences, especially for small test sets. | The dataset is the unit of analysis, and the paired Wilcoxon test across 91 datasets is the inferential procedure. A seed-variability analysis on 30 datasets (seeds 0–2) is reported in Sect. 6.9 (E1 seeds 1–2). |
| 3 | MODERATE | *Baseline tuning.* LightGBM and GRU-D use fixed settings, and the ROCKET family uses library defaults. A reader might suspect weak baselines. | All ROCKET-family methods share MissRocket's ridge head with LOO-selected penalty. Their defaults are the published, recommended settings. LightGBM and GRU-D use common settings (GRU-D with early stopping); neither was tuned, and neither was MissRocket on confirmatory data. GRU-D and LightGBM *win* on PhysioNet 2012, which argues against systematic weakening. Stated in Sect. 5.3; limitation 7 extended. |
| 4 | MODERATE | *Power of the subset experiments.* E3 (ablation) and E4 (shift) use 30 datasets; Holm over 12 comparisons is conservative. Non-significant cells (e.g. MNAR weighting at 50% in E3) must not be read as "no effect". | Sentence added to Sect. 6.2: non-significance on 30 datasets is inconclusive, and the full-benchmark comparison with γ=0 (Table 2) is the primary ablation evidence. |
| 5 | MODERATE | *Ties.* Many small UCR test sets produce ties. | The zero_method="zsplit" handling is stated in Sect. 5.5. Ties are reported in W/T/L. No change. |
| 6 | MINOR | *Bootstrap p-values on PhysioNet 2012* are reported as "<0.001" from 2,000 resamples. The resolution is 1/2000. | The caption now states the number of resamples, and "<0.001" means that no resample favoured the other sign. |
| 7 | MINOR | *Selection-variant tables* (S9) report γ frequencies for E3 only. | Fine. |

## Leakage audit (re-checked against code)

| Check | Code location | Status |
|---|---|---|
| kNN imputer fit on training only | `methods._knn_pre`, `missrocket.fit` | OK |
| P12 standardisation from training stays | `e5_p12.run` | OK |
| Bias sampling from training series only | `MissRocket.fit` | OK |
| Ridge α and γ selection on training only | `RidgeClassifierCV`, `MissRocket.fit` | OK |
| Independent train/test masks | `runner.corrupt` (different hashed seeds) | OK |
| Development/confirmatory separation | `data/registry.csv`; dev datasets excluded from `confirmatory_datasets()` | OK |

## Author response

Issues 1, 3, 4 and 6 are fixed in the text and code. Issue 2 is addressed by Sect. 6.9 once seeds 1–2 have completed.
