# Phase 3: Literature Matrix (verified references only)

All entries were bibliographically verified (Crossref DOI, arXiv API or PubMed); see `supplementary/citation_audit_*.csv`. Facts about content come from the papers' own abstracts or main text as read during this study. Where a detail was not checked, the cell says "n/c" (not checked); no detail was guessed.

## A. Random-convolution and strong TSC methods (complete data)

| Paper | Venue | Problem | Data | Method | Missing values? | Code | Gap relevant to us |
|---|---|---|---|---|---|---|---|
| Dempster et al. 2020 (ROCKET) | DMKD 34 | univariate/multivariate TSC | UCR (85 / 128 sets) | 10k random kernels, PPV + max pooling, ridge/logistic | Not handled; complete equal-length input assumed | yes | Transform undefined for NaN |
| Dempster et al. 2021 (MiniRocket) | KDD 2021 | fast TSC | UCR 109 (+ equal-length) | 84 fixed kernels {−1,2}, dilations, PPV, ridge | Not handled | yes | Kernel weights sum to zero, so the response is a group-mean contrast. **We exploit this.** |
| Tan et al. 2022 (MultiRocket) | DMKD 36 | TSC | UCR 128 equal-length subset | MiniRocket kernels + 4 pooling ops + first-difference input | Not handled | yes | — |
| Dempster et al. 2023 (Hydra) | DMKD 37 | TSC | UCR | competing random kernels (dictionary-like counts) | Not handled | yes | — |
| Dempster et al. 2024 (QUANT) | DMKD 38 | TSC | UCR 142 | interval quantiles + extra-trees | Not handled | yes | — |
| Middlehurst et al. 2024 (Bake-off redux) | DMKD 38 | benchmark | 112 UCR + 30 new | 20+ algorithms, Wilcoxon/Holm critical-difference diagrams | Excludes series with missing values or unequal length | yes (aeon) | Benchmark practice excludes the very datasets where missing values arise |
| Middlehurst et al. 2021 (HIVE-COTE 2) | Mach Learn 110 | TSC ensemble | UCR | meta-ensemble | Not handled | yes | — |
| Bagnall et al. 2017 | DMKD 31 | benchmark | UCR 85 | 18 algorithms | n/a | yes | — |
| Dau et al. 2019 | IEEE/CAA JAS 6 | UCR 2018 archive | 128 datasets | archive | Provides 15 variable-length / missing datasets | — | Natural incomplete data source |
| Ismail Fawaz et al. 2019 | DMKD 33 | deep TSC review | UCR/UEA | FCN, ResNet, … | Not handled | yes | — |
| Wang et al. 2017 (FCN) | IJCNN | deep baseline | UCR | FCN/ResNet | Not handled | yes | — |
| Ismail Fawaz et al. 2020 (InceptionTime) | DMKD 34 | deep TSC | UCR | Inception ensemble | Not handled | yes | — |

## B. Learning with missing values / irregular time series

| Paper | Venue | Approach | Data | Compared with ROCKET family? | Notes |
|---|---|---|---|---|---|
| Che et al. 2018 (GRU-D) | Sci Rep 8 | GRU with decay toward empirical mean; mask and time-gap inputs | PhysioNet 2012, MIMIC-III, synthetic | No | Informative missingness exploited via the mask |
| Lipton et al. 2016 | arXiv 1606.04130 (MLHC) | RNN with missingness indicators | clinical time series (PICU) | No | Indicators improve classification |
| Cao et al. 2018 (BRITS) | arXiv 1805.10572 (NeurIPS) | bidirectional recurrent imputation + classification | health, air quality, activity | No | — |
| Du et al. 2023 (SAITS) | ESWA 219 | self-attention imputation | PhysioNet 2012, air quality, electricity | No | Imputer only |
| Shukla & Marlin 2021 (mTAN) | arXiv 2101.10318 (ICLR) | multi-time attention for irregular series | PhysioNet 2012, MIMIC-III | No | — |
| Zhang et al. 2022 (Raindrop) | arXiv 2110.05357 (ICLR) | graph-guided network for irregular multivariate series | P19, P12, PAM | No | — |
| Horn et al. 2020 (SeFT) | arXiv 1909.12064 (ICML) | set functions over observations | P12, MIMIC-III | No | — |
| Kidger et al. 2020 (Neural CDE) | arXiv 2005.08926 (NeurIPS) | continuous-time controlled differential equations | CharacterTrajectories (dropped), Speech Commands, P19 | No | — |
| Mikalsen et al. 2018 (TCK) | Pattern Recognit 76 | GMM-ensemble kernel for MTS with missing data | UCR/UEA-derived + clinical | No | Shows ignoring missingness can beat biased imputation |
| Yao et al. 2024 | arXiv 2408.05849 | end-to-end GRU imputation + multi-scale CNN | 68 UCR (MCAR 20–80%), PAM, 4 natural | **No** (deep baselines only) | Strongest direct competitor on UCR + MCAR. No ROCKET baseline, MCAR only. |
| Spinnato & Landi 2025 (PYRREGULAR) | arXiv 2505.06047 | benchmark library for irregular series | 34 naturally irregular datasets | Includes sktime MiniRocket with NaNs passed to LightGBM | MiniRocket ranks **first** overall, but the transform is not adapted to missingness |
| Le Morvan et al. 2021 | arXiv 2106.00311 (NeurIPS) | theory: impute-then-regress | synthetic + tabular | n/a | Almost any imputation is Bayes-consistent with a flexible enough learner |
| Josse et al. 2019 | arXiv 1902.06931 | consistency of supervised learning with missing values | theory + sims | n/a | Constant imputation + indicator is consistent for flexible learners |
| Van Ness et al. 2023 | KDD 2023 | missing-indicator method in high dimensions | tabular | n/a | Indicators help under informative missingness; selective indicators |
| Perez-Lebel et al. 2022 | GigaScience 11 | benchmark of missing-value handling | health databases | n/a | Native handling and indicators often beat sophisticated imputation |
| Twala et al. 2008 | Pattern Recognit Lett 29 | missing data in decision trees (MIA) | UCI | n/a | Basis of native NaN handling in GBDT |
| Liu et al. 2018 (partial conv) | ECCV | mask-renormalised convolution for inpainting | images | n/a | **Rescaling by 9/|O| breaks zero-sum kernels.** We compare against it. |
| Rubin 1976; Little & Rubin 2019 | Biometrika; Wiley | MCAR/MAR/MNAR taxonomy | — | — | Mechanisms used in our simulation |

## C. Evaluation methodology

Demšar 2006 (JMLR) and Benavoli et al. 2016 (JMLR) argue for Wilcoxon signed-rank tests over datasets rather than post-hoc tests on mean ranks. We use Wilcoxon (1945) and Holm (1979).

## Gap synthesis (Phase 3 questions)

**WHAT EXISTS?**
- ROCKET-family transforms that are fast and accurate on complete data.
- Deep missing-aware models (GRU-D, BRITS, Raindrop, mTAN, SeFT, CDE).
- An end-to-end deep model evaluated on UCR with MCAR (Yao et al. 2024).
- A benchmark showing MiniRocket is the strongest model on naturally irregular data even without adaptation (PYRREGULAR).
- Theory that impute-then-predict plus indicators is consistent for *flexible* learners.

**WHAT IS MISSING?**
1. No study isolates *where* and *how* missingness should enter a random-convolution transform. The candidate strategies are: imputing before it, estimating kernel responses from observed taps, renormalising, weighting the pooling, or adding mask features.
2. No large-scale evidence spans different mechanisms (MCAR vs long-gap block vs value-dependent MNAR).
3. No train–test missingness-shift evaluation exists for these classifiers.
4. No comparison of ROCKET-family + imputation against deep missing-aware models has been made under one protocol.
5. Theory assumes flexible learners, whereas ROCKET-family classifiers use fixed random features + a linear head, so the theory does not directly apply.

**WHY IT MATTERS.** ROCKET-family classifiers are the default practical choice (speed, accuracy), and real sensor data have gaps. A wrong handling choice can silently cost accuracy, as our development set shows: zero-filling loses 20+ points on ArrowHead.

**WHAT THIS RESEARCH ADDS.** See `03_novelty_map.md` and `04_hypotheses_and_experiments.md`.
