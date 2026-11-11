# Phase 4: Prior-Art and Novelty Map

## Searches performed (2026-11-10/11)

Web and arXiv searches combined these terms:

- "MiniRocket/ROCKET + missing values / NaN / mask / without imputation"
- "random convolutional kernels + missing data + partial/masked convolution"
- "aeon/sktime missing-value capability for MultiRocket/Hydra/QUANT"
- "time series classification missing values benchmark UCR imputation"
- "early classification conformal / risk control" (for the rejected direction #1)

Primary sources were read for the two closest works: PYRREGULAR (arXiv 2505.06047) and Yao et al. (arXiv 2408.05849). Patent search: one US patent on joint impute-and-learn for prediction surfaced in the web results; it is a deep joint imputation model, not a convolution-transform modification.

## Map

| Existing work | Contribution | Relation to this work |
|---|---|---|
| ROCKET / MiniRocket / MultiRocket / Hydra / QUANT (Dempster et al.; Tan et al.) | Fast random/fixed-kernel transforms for complete, equal-length series | We use their kernels unchanged. New: the response is defined for incomplete input, and pooling is reliability-weighted. |
| POCKET / P-ROCKET (kernel pruning) | Kernel selection; zero-fill for missing values | Zero-fill is one of our baselines; no missingness modelling there. |
| PYRREGULAR (Spinnato & Landi 2025) | Benchmark of irregular-series classifiers; MiniRocket via sktime with NaNs passed to LightGBM; MiniRocket ranks first | No transform adaptation and no simulated mechanisms or rates. We adapt the transform and study mechanisms, rates and shift. |
| Yao et al. 2024 (arXiv) | End-to-end GRU imputation + multi-scale CNN on 68 UCR datasets (MCAR) | Deep, GPU-trained, MCAR only, no ROCKET-family baselines. We are CPU-cheap, cover 3 mechanisms and use ROCKET-family + GRU-D baselines. |
| GRU-D, BRITS, SAITS, mTAN, Raindrop, SeFT, Neural CDE | Deep missing-aware or irregular-series models | GRU-D is included as the deep baseline (UCR subset + P12). |
| Partial convolution (Liu et al. 2018) | Mask-renormalised convolution for image inpainting | We show renormalisation breaks MiniRocket's zero-sum structure. We compare it in development and propose the group-mean form instead. |
| Missing-indicator literature (Lipton 2016; Josse 2019; Le Morvan 2021; Van Ness 2023) | Impute + indicators is consistent with flexible learners; indicators help under informative missingness | Our mask-pattern features are a time-series analogue. Their inclusion is selected per dataset and ablated. |
| Learn-then-Test early classification (Ringel et al. 2024) | Risk-controlled stopping | Unrelated task; recorded as the rejected direction #1. |

## Genuinely different elements (claims we will make, and only these)

1. The zero-sum/group-mean formulation of MiniRocket responses for incomplete series, with exact complete-data equivalence, offset invariance and MCAR unbiasedness. No prior work found.
2. Observed-tap-count-weighted PPV pooling, with γ selected on training data via ridge LOO and all γ computed from per-count exceedance histograms in one pass. No prior work found.
3. The first pre-registered, multi-mechanism, multi-rate evaluation of missing-value handling for ROCKET-family classifiers, including negative results for native estimators.

## Claims we will NOT make

- "First to handle missing values in TSC". False: deep models exist.
- "State of the art for TSC with missing values". Not established: we do not compare against every deep model on GPU-scale settings.
- Any superiority claim not backed by the confirmatory statistics.
