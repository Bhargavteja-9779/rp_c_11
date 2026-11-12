## 1 Introduction

Time series classification (TSC) underpins applications such as industrial monitoring, wearable and clinical sensing, and remote sensing. In these settings the data are rarely complete. Sensors drop out for minutes or hours, communication links lose packets, values beyond an instrument's range are not recorded, and clinical variables are measured only when a clinician orders them. The resulting gaps differ in length, in how they relate to the signal, and in whether they carry information about the class.

Among accurate TSC methods, random-convolution transforms are the practical reference point. ROCKET [@Dempster2020], MiniRocket [@Dempster2021], MultiRocket [@Tan2022] and Hydra [@Dempster2023] reach accuracy close to the heaviest ensembles at a small fraction of their cost [@Middlehurst2024]. All of them, however, are defined for complete, equal-length input. In practice, missing values are therefore handled by ad-hoc preprocessing:

- the series is zero-filled or interpolated before the transform;
- or the incomplete datasets are simply excluded from benchmarks [@Bagnall2017; @Middlehurst2024].

When NaNs are passed through such a transform, the downstream learner must cope with whatever the transform produces [@Spinnato2025]. Deep missing-aware models exist [@Che2018; @Shukla2021; @Zhang2022; @Yao2024], but they are far costlier to train and tune, and they have rarely been compared with random-convolution pipelines under one protocol.

This leaves a practical and a scientific question open:

- *How should missingness enter a random-convolution transform?*
- Is imputation followed by the transform adequate?
- Should the transform estimate its kernel responses from the observed values only?
- Or should it treat responses that rely on missing data differently?

The answer is not obvious. Statistical theory shows that impute-then-predict is consistent when the learner is flexible enough [@Josse2019; @LeMorvan2021]. Random-convolution classifiers, however, are fixed feature maps followed by a linear model, so the way missingness enters the feature map matters directly.

This paper studies the question for MiniRocket, the simplest and fastest member of the family.

- **The kernel response as a contrast of means.** The zero-sum MiniRocket kernel response is a scaled difference of two tap-group means (Section 3.2). This yields a native estimator from observed taps that is exact on complete data, invariant to the series level, and unbiased under MCAR. It also shows why renormalised (partial) convolutions are ill-suited to these kernels.
- **Interpolation fails in a specific way.** Interpolation produces low-variance but *fabricated* responses inside long gaps (Proposition 3). This motivates **MissRocket**: interpolated responses are retained, but each response's contribution to the proportion-of-positive-values pooling is weighted by the fraction of its taps that were actually observed.
- **The method adds no learnable parameters.** It reduces exactly to MiniRocket on complete data, and costs about the same as MiniRocket.

Our contributions are:

1. A formal treatment of missingness inside MiniRocket kernels: exactness, offset invariance, unbiasedness and the variance of a native estimator; the failure of partial-convolution renormalisation; and the fabricated-response property of interpolation (Section 4).
2. **MissRocket**, an observed-tap-weighted pooling scheme that requires no imputation model and no training beyond the usual ridge head (Section 4.2).
3. A pre-specified evaluation with a separate development set. It covers {{N_CONF}} UCR datasets, three missingness mechanisms (MCAR, contiguous gaps and value-dependent MNAR) at three rates, and twelve competitors, including reference MiniRocket, MultiRocket and Hydra with five imputation strategies, LightGBM with native missing-value handling, and GRU-D. It also includes ablations, train–test missingness shift, 15 naturally incomplete UCR datasets and PhysioNet 2012 mortality prediction (Sections 5–6).
4. Evidence on where each strategy succeeds and fails:
   - observed-tap weighting helps substantially when gaps are long, when missingness depends on the values, and under train–test missingness shift;
   - it neither helps nor materially hurts under scattered random gaps;
   - native estimation is consistently inferior to interpolation;
   - cross-series kNN imputation and clinical-specific models are better in their respective niches (Sections 6–7).

All code, raw per-run results and the scripts that generate every number, table and figure are released.
