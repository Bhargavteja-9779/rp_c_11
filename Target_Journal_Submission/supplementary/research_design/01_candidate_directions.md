# Phases 1–2: Candidate Research Directions and Stress Test

> Note: works named in this internal screening table but not in `manuscript/references.json` (Sarhan et al., Hendriks et al., Wu & Keogh, Kim et al. 2022, Elor & Averbuch-Elor, Dhariyal et al., Transcend/TESSERACT) were used only for internal screening. They are **not cited in the manuscript** and were not bibliographically verified.

Constraints that shaped the screen:

- **Hardware:** 4 CPU cores, no GPU, 15 GB RAM.
- **Journal:** JKSU-CIS, which takes ML / signal-processing / pattern-recognition method papers.
- **Data:** public only.
- **Evidence standard:** multi-dataset evidence with statistical testing must be feasible.

| # | Direction | Data | Main reason kept / rejected |
|---|---|---|---|
| 1 | Distribution-free risk-controlled early time-series classification (Learn-then-Test stopping rules) | UCR | **Rejected (prior art).** Ringel et al. (arXiv 2402.00857, ICML 2024) already apply LTT to ETSC, and a semi-supervised extension exists (arXiv 2412.11174). |
| 2 | Cross-dataset generalisation of NetFlow intrusion detectors | NF-v2 datasets | Rejected: cross-dataset evaluation on the shared NetFlow feature set already exists (Sarhan et al.), and NIDS benchmarks have known label-quality problems. High incremental risk. |
| 3 | Conformal / selective prediction for intrusion detection under drift | CIC-IDS2017 | Rejected: conformal evaluation for security drift (Transcend/TESSERACT line) already exists. |
| 4 | Multi-label ECG classification with cross-site shift (PTB-XL → PhysioNet 2021) | PhysioNet | Rejected for feasibility: deep 12-lead models with multiple seeds and baselines are infeasible on 4 CPUs in the time available. |
| 5 | Cross-subject human activity recognition | UCI-HAR, PAMAP2 | Rejected: saturated literature, small subject counts, incremental-novelty risk. |
| 6 | Bearing-fault cross-condition diagnosis | CWRU, Paderborn | Rejected: saturated, with known segment-leakage issues already documented (Hendriks et al. 2022). |
| 7 | Time-series anomaly-detection evaluation (point-adjust bias) | SMD, SWaT | Rejected: flaws already documented (Wu & Keogh 2021; Kim et al. 2022). |
| 8 | SMOTE variants for tabular imbalance | OpenML | Rejected: "strong classifier beats SMOTE" already shown (Elor & Averbuch-Elor 2022). |
| 9 | Calibration of ROCKET-family classifiers | UCR | Deferred: feasible, but the contribution is mainly an evaluation of post-hoc calibration, so incremental. |
| 10 | Channel selection for multivariate TSC | UEA | Rejected: classifier-agnostic channel selection already exists (Dhariyal et al. 2023). |
| 11 | Label-noise robustness in TSC | UCR | Deferred: feasible, moderate novelty. |
| 12 | EEG motor-imagery cross-subject alignment | MOABB | Rejected: saturated (Euclidean alignment and its variants). |
| 13 | Sleep staging with single-channel EEG | Sleep-EDF | Rejected: compute- and saturation-limited. |
| 14 | Federated learning on non-IID clinical time series | P12 | Rejected: compute- and evaluation-limited, incremental. |
| 15 | **Missing values in random-convolution (ROCKET-family) time-series classification** | UCR 2018 (113 complete + 15 naturally incomplete) | **SELECTED.** See below. |
| 16 | Variable-length handling for ROCKET-family | UCR variable-length | Merged into #15: variable length is treated as trailing missingness. |

## Why #15 survived the editor stress test (Phase 2)

- **Real problem, real gap.** ROCKET-family classifiers are the speed/accuracy reference in TSC (Middlehurst et al. 2024), yet they require complete, equal-length input. Current practice is ad hoc:
  - POCKET zero-fills.
  - The standard UCR benchmark excludes the 15 incomplete datasets.
  - PYRREGULAR (Spinnato & Landi 2025) passes NaNs through sktime MiniRocket and relies on a downstream LightGBM.
  - The deep end-to-end model of Yao et al. (2024) never compares against ROCKET-family baselines.
  - No study isolates *how* missingness should enter the transform.
- **Testable hypotheses with objective evidence.** 103 confirmatory datasets × 3 mechanisms × 3 rates × 5 seeds, plus naturally incomplete data, support well-powered Wilcoxon/Holm testing across datasets.
- **Strong, cheap baselines.** Several imputation strategies + MiniRocket/MultiRocket/Hydra, LightGBM with native NaN handling, 1-NN, and GRU-D.
- **Simpler-method risk** ("could linear interpolation do as well?") is not a threat to hide. It is the central research question and is answered experimentally, including negative results.
- **Leakage risk is low.** Fixed archive splits are used, missingness is simulated independently for train and test, and imputers are per-series or fit on train only.
- **Editor-level risk, stated plainly.** If the proposed estimators do not beat interpolation, the paper's contribution shifts to (i) a principled estimator family with proven properties, (ii) a definitive large-scale answer on how missingness should be handled in the transform, and (iii) the regime map of when each strategy wins. That would be a benchmark-plus-method paper. This risk is tracked in the rejection-risk report.
