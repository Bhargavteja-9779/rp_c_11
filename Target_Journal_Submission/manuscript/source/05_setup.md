## 5 Experimental setup

### 5.1 Data

**UCR archive.** We use the 2018 UCR archive [@Dau2019] with its fixed train/test splits. Of the 113 complete, equal-length datasets:

- 10 form a *development set* used for every design decision. These are the five datasets used for an initial feasibility pilot (ArrowHead, GunPoint, ECG200, Wafer, ShapesAll) plus five drawn at random with a fixed seed (CinCECGTorso, MoteStrain, MixedShapesSmallTrain, DistalPhalanxOutlineAgeGroup, MiddlePhalanxOutlineAgeGroup).
- The remaining 103 form the *confirmatory set*. A compute rule fixed before any confirmatory run (at most 2,000 training series and 2×10⁶ values in total) retains {{N_CONF}} of them. The excluded datasets are {{EXCLUDED_LIST}}.

The 15 archive datasets with native missing values (4) or variable lengths (11) are used without simulation in Section 6.5. Variable-length series are represented by trailing missing values.

**PhysioNet/CinC 2012.** The challenge data [@Silva2012; @Goldberger2000] contain 12,000 intensive-care stays (sets a, b and c) with outcomes. We bin 37 time-varying variables into 48 hourly intervals; a bin with no measurement is missing. This gives 79.7% missing entries, missingness that is informative by nature, and 14.2% in-hospital mortality. Sets a and b (8,000 stays) are used for training and set c (4,000 stays) for testing. Variables are standardised with training statistics. Static descriptors are not used by any method.

### 5.2 Missingness simulation

Missingness is simulated independently for every series. Training and test masks are generated with different seeds, derived by hashing the dataset, mechanism, rate, seed and split, so every method sees exactly the same corrupted data. Three mechanisms are used:

- **MCAR:** each point is removed independently with probability $r$.
- **Block:** contiguous gaps of geometric length with mean 10% of the series length, placed uniformly until a fraction $r$ is removed. This models sensor dropout.
- **MNAR (self-masking):** $P(\text{missing})=\sigma(a+2z_t)$, where $z_t$ is the standardised value and $a$ is solved per series so that the expected fraction equals $r$. High values are preferentially lost, as with saturation.

We use $r\in\{0.2,0.5,0.8\}$ and keep at least two observed points per series. Unit tests verify the realised rates.

### 5.3 Methods compared

All ROCKET-family methods use the standard ridge head (standardisation followed by `RidgeClassifierCV` from scikit-learn [@Pedregosa2011], $\alpha\in\{10^{-3},\dots,10^3\}$).

1. **Proposed: MissRocket.** Linear gap filling, MiniRocket kernels (10,000 features) and observed-tap-weighted PPV with $\gamma=1$ (Section 4.2).
2. **Imputation + reference MiniRocket.** The aeon implementation [@Middlehurst2024aeon] after:
   - linear interpolation;
   - zero filling;
   - per-series mean filling;
   - LOCF;
   - cross-series k-nearest-neighbour imputation ($k=5$), fit on the training set.
3. **Stronger convolution classifiers after linear interpolation:** MultiRocket [@Tan2022] and Hydra concatenated with MultiRocket [@Dempster2023], both from aeon. These are among the most accurate convolution-based methods in the recent bake-off [@Middlehurst2024].
4. **Native estimator:** the group-mean MiniRocket of Section 4.1, which uses no imputation.
5. **Conventional ML with native missing-value handling:** LightGBM [@Ke2017] on the raw time points (300 trees, learning rate 0.05, 31 leaves, `min_child_samples`=5, row subsampling 0.8, column subsampling 0.5). On PhysioNet 2012, with 8,000 training stays, we used 500 trees, learning rate 0.03 and `min_child_samples`=20.
6. **Classical baseline:** 1-NN with Euclidean distance after linear interpolation.
7. **Deep missing-aware baseline:** GRU-D [@Che2018] with 64 hidden units, Adam (learning rate $10^{-3}$), early stopping (patience 8 epochs, restoring the best weights) on a stratified 20% validation split of the training data, and at most 60 epochs. On UCR it is run on a pre-specified subset (length ≤ 300, at most 500 training series; rate 0.5; seed 0) because of CPU cost. It is also run on PhysioNet 2012.

**Ablations** (Section 6.2) use the same pipeline with one change each:

- $\gamma=0$, which is linear interpolation + MiniRocket in our implementation;
- $\gamma\in\{0.5,2\}$;
- adding missingness-pattern features;
- selecting $(\gamma,\text{mask})$ on the training set by leave-one-out;
- replacing linear interpolation by zero filling, LOCF or kNN, each with and without weighting.

No method's hyperparameters were tuned on confirmatory data. Baseline settings are the library defaults, or the defaults stated above.

### 5.4 Protocol, pre-specification and amendments

**Development phase.** Design choices were made on the 10 development datasets only (seed 0; MCAR, block and MNAR at rates 0.3 and 0.6). The choices covered:

- the estimator family: native group-mean, partial convolution, gap-adaptive hybrid, feature fusion and reliability weighting;
- the value $\gamma=1$;
- the default exclusion of mask features.

All candidates and their development results are documented in Online Resource 1, including the negative results.

**Pre-specification.** The experimental protocol (datasets, mechanisms, rates, seeds, methods, metrics and tests) was then frozen in a version-controlled configuration before any confirmatory run. We use "pre-specified" rather than "pre-specified" because the protocol was not lodged with an external registry. The freezing commit is identified in the code repository.

**Disclosed deviations.** Three deviations occurred, none of which changed the proposed method:

1. *Smoke test on confirmatory data.* Before the freeze, a pipeline smoke test ran on three confirmatory datasets (Coffee, ItalyPowerDemand, SyntheticControl). It prompted us to screen kNN-filled variants on the development set and add them to the ablations.
2. *Execution order.* The frozen protocol specified three seeds for E1 and all experiments on all eligible datasets. Our cloud environment reclaims idle compute containers, which repeatedly interrupted long runs. We therefore changed the execution order, running seed 0 first.
3. *Rescoped experiments.* We then rescoped the study:
   - the primary benchmark E1 uses seed 0 on all {{N_CONF}} eligible datasets;
   - seeds 1 and 2 were run only on a random subset of 30 eligible datasets drawn with a fixed seed (Online Resource 1), for the seed-variability analysis of Section 6.9;
   - the ablation (E3) and shift (E4) experiments use the same subset; E3 is run at rate 0.5;
   - PhysioNet 2012 uses one seed with a patient-level bootstrap;
   - GRU-D on UCR is restricted to series of length ≤ 200 with at most 300 training series.

Amendments 2 and 3 were decided and committed while only run counts and run times, and no accuracy values, of the confirmatory experiments had been inspected.

**Seeds.** A seed controls the missingness masks and the bias sampling of the transforms.

### 5.5 Metrics and statistical analysis

The primary metric is test accuracy. Balanced accuracy and macro-F1 are also reported. For PhysioNet 2012 we report AUROC and AUPRC.

**Unit of analysis.** For UCR, the dataset is the unit of analysis. The primary analyses use seed 0. The natural datasets were run with three seeds, and their accuracies are averaged over seeds before testing.

**Tests.** For each mechanism–rate condition we used:

- the two-sided Wilcoxon signed-rank test [@Wilcoxon1945], with zero differences split, as recommended for comparing classifiers over multiple datasets [@Demsar2006; @Benavoli2016];
- Holm's step-down correction [@Holm1979] over the family of comparisons of MissRocket against all baselines within the condition.

**Effect sizes:**

- mean and median paired difference;
- percentile-bootstrap 95% confidence interval of the mean difference, from 10,000 resamples of datasets;
- matched-pairs rank-biserial correlation;
- win/tie/loss counts.

**Multiplicity.** Each mechanism–rate condition is treated as a separate, pre-specified question, and Holm's correction controls the family-wise error rate within a condition only. The pooled comparison over all nine conditions serves as the single overall test. Per-condition p-values describe where an effect appears and should not be read as nine independent confirmations.

**PhysioNet 2012.** Patients are the unit of analysis. We give a paired bootstrap (2,000 resamples) of the AUROC difference between seed-averaged score ensembles.

**Timing.** Wall-clock time was measured on a 4-core CPU with no GPU.

**Use of AI tools.** In line with the journal's policy, we document that an AI agent (Anthropic Claude) assisted with the literature search, the implementation of the code, experiment orchestration, analysis scripting and drafting. Every number in this paper is produced by the released code from the raw outputs, and every reference was verified against bibliographic databases (see Statements and Declarations).
