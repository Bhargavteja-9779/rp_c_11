# Phases 5–8: Hypotheses, Research Questions, Experimental Design, Dataset and Leakage Audit

**Status:** frozen before any confirmatory run. Development-set evidence that motivated the design is in `results/dev/dev_screening_v2.csv`, which is the frozen-code rerun; see PROGRESS.md item 7.

## Scientific contribution (precise)

1. **A missingness-aware formulation of MiniRocket's kernel response.** Because MiniRocket weights sum to zero, the response is a scaled contrast of two tap-group means, C = 6(mean_P − mean_Q). From this we derive two properties:
   - a native estimator from observed taps that is bit-exact on complete data, invariant to the series offset, and conditionally unbiased under MCAR;
   - the observation that partial-convolution renormalisation breaks the zero-sum (offset-invariance) property.
2. **MissRocket.** Linear gap filling, then MiniRocket responses, then *observed-tap-weighted* PPV pooling with weight (c/9)^γ, where c is the number of truly observed taps. Optional missingness-pattern features are added. γ and the mask option are chosen on the training set with the ridge head's leave-one-out (GCV) criterion. The family contains interpolation + MiniRocket exactly (γ = 0, no mask). All γ are computed in a single pass via per-count exceedance histograms.
3. **A large, pre-registered evaluation** of how missingness should enter random-convolution TSC:
   - 91 confirmatory UCR datasets;
   - 3 mechanisms × 3 rates × 3 seeds;
   - 15 baselines and ablations;
   - train/test rate shift;
   - 15 naturally incomplete UCR datasets;
   - PhysioNet 2012.
   It reports where each strategy wins and includes negative results for the native estimators.

## Hypothesis

H: Observed-tap-weighted pooling with training-selected strength improves accuracy over interpolation + MiniRocket when gaps are long (block missingness), without a material loss under short-gap MCAR. The selection can fall back to γ = 0.

## Research questions → experiments

| RQ | Question | Experiment | Primary evidence |
|---|---|---|---|
| RQ1 | Does MissRocket improve on the strongest practical pipelines (reference MiniRocket/MultiRocket/Hydra with imputation) across mechanisms and rates? | E1 (main), E2 (GRU-D subset) | Wilcoxon + Holm per condition, bootstrap CI of mean paired difference, win/tie/loss |
| RQ2 | Which component matters (weighting, γ selection, mask features)? | E1 ablations | Same statistics vs each ablation |
| RQ3 | Can native no-imputation estimators compete with interpolation, and why or why not? | E1 (MaskRocket-noC), dev log, error analysis | Paired differences and the bias–variance explanation |
| RQ4 | Is the method robust when train and test missingness differ? | E4 | Paired tests per shift pair |
| RQ5 | Does it generalise to naturally incomplete data and multivariate clinical series with informative missingness? | E5a (15 UCR natural), E5b (PhysioNet 2012) | Paired tests; AUROC/AUPRC with patient-level bootstrap |
| RQ6 | What does it cost? | All runs (timing), E7 | Fit/predict time, feature counts, sensitivity to feature budget and γ grid |

Additional analyses:
- **Error analysis (E8):** per-dataset gains vs dataset properties (length, train size, classes, mean gap length); selected γ by mechanism; worst-case datasets.

## Datasets (Phase 7)

- **UCR 2018 archive** (Dau et al. 2019): 128 univariate datasets with fixed train/test splits, widely used as a benchmark.
  - 113 complete datasets: 10 development + 103 confirmatory. 91 confirmatory datasets meet the pre-registered compute rule (≤ 2M points and n_train ≤ 2000).
  - The 12 excluded datasets are listed in the paper.
  - The 15 datasets with native missing values or variable length are used for E5a.
- **PhysioNet/CinC 2012** (Silva et al. 2012; Goldberger et al. 2000): 12,000 ICU stays, 37 variables binned hourly over 48 h, 79.7% missing, 14.2% in-hospital mortality. Licence: Open Data Commons Attribution v1.0. Split: sets a+b train, set c test.

## Leakage audit (Phase 8)

| Risk | Status |
|---|---|
| Train/test overlap | UCR official splits; PhysioNet sets a/b vs c are disjoint patient sets. |
| Preprocessing leakage | Per-series imputers use only that series. The kNN imputer and P12 standardisation are fit on training data only. Biases, γ, mask option and ridge α are all chosen from training data. |
| Simulation leakage | Train and test masks use different hashed seeds and are generated independently. Every method sees identical corrupted data within a setting. |
| Design leakage | Design choices were made only on 10 development datasets. The confirmatory set was not inspected before freezing. |
| Seed selection | Seeds {0,1,2} fixed in advance; all seeds are reported (seed-averaged per dataset). |
| Duplicates within UCR | Not audited by us; inherited from the archive (stated as a limitation). |
| Label leakage via missingness (P12) | Missingness is informative by nature (clinical ordering). This is part of the task, and all methods may use it equally. |
