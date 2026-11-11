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

All ROCKET-family methods use the standard ridge head (standardisation followed by `RidgeClassifierCV`, $\alpha\in\{10^{-3},\dots,10^3\}$).

1. **Proposed: MissRocket.** Linear gap filling, MiniRocket kernels (10,000 features) and observed-tap-weighted PPV with $\gamma=1$ (Section 4.2).
2. **Imputation + reference MiniRocket.** The aeon implementation [@Middlehurst2024aeon] after:
   - linear interpolation;
   - zero filling;
   - per-series mean filling;
   - LOCF;
   - cross-series k-nearest-neighbour imputation ($k=5$), fit on the training set.
3. **Stronger convolution classifiers after linear interpolation:** MultiRocket [@Tan2022] and Hydra concatenated with MultiRocket [@Dempster2023], both from aeon. These are among the most accurate convolution-based methods in the recent bake-off [@Middlehurst2024].
4. **Native estimator:** the group-mean MiniRocket of Section 4.1, which uses no imputation.
5. **Conventional ML with native missing-value handling:** LightGBM [@Ke2017] on the raw time points (300 trees, learning rate 0.05, 31 leaves, `min_child_samples`=5, row and column subsampling).
6. **Classical baseline:** 1-NN with Euclidean distance after linear interpolation.
7. **Deep missing-aware baseline:** GRU-D [@Che2018] with 64 hidden units, Adam (learning rate $10^{-3}$), early stopping on a stratified 20% validation split of the training data, and at most 60 epochs. On UCR it is run on a pre-registered subset (length ≤ 300, at most 500 training series; rate 0.5; seed 0) because of CPU cost. It is also run on PhysioNet 2012.

**Ablations** (Section 6.2) use the same pipeline with one change each:
- $\gamma=0$, which is linear interpolation + MiniRocket in our implementation;
- $\gamma\in\{0.5,2\}$;
- adding missingness-pattern features;
- selecting $(\gamma,\text{mask})$ on the training set by leave-one-out;
- replacing linear interpolation by zero filling, LOCF or kNN, each with and without weighting.

No method's hyperparameters were tuned on confirmatory data. Baseline settings are the library defaults, or the defaults stated above.

### 5.4 Protocol and pre-registration

Design choices were made on the 10 development datasets only (seed 0; MCAR, block and MNAR at rates 0.3 and 0.6). The choices covered:
- the estimator family: native group-mean, partial convolution, gap-adaptive hybrid, feature fusion and reliability weighting;
- the value $\gamma=1$;
- the default exclusion of mask features.

All candidates and their development results are documented in the supplementary development log, including the negative results. The experimental protocol (datasets, mechanisms, rates, seeds, methods, metrics and tests) was then frozen in a version-controlled configuration before any confirmatory run. One deviation is disclosed. A pipeline smoke test ran on three confirmatory datasets (Coffee, ItalyPowerDemand, SyntheticControl) before the freeze. It led us to add kNN-filled variants to the ablations after screening them on the development set; it did not change the proposed method.

E1 used three seeds (0, 1 and 2) fixed in advance. A seed controls the missingness masks and the bias sampling of the transforms. The ablation experiment E3 used seed 0.

### 5.5 Metrics and statistical analysis

The primary metric is test accuracy. Balanced accuracy and macro-F1 are also reported. For PhysioNet 2012 we report AUROC and AUPRC.

**Unit of analysis.** For UCR, the dataset is the unit of analysis. Accuracies are first averaged over seeds, and the per-dataset paired differences are then tested.

**Tests.** For each mechanism–rate condition we used:
- the two-sided Wilcoxon signed-rank test [@Wilcoxon1945], with zero differences split, as recommended for comparing classifiers over multiple datasets [@Demsar2006; @Benavoli2016];
- Holm's (1979) correction over the family of comparisons of MissRocket against all baselines within the condition.

**Effect sizes:**
- mean and median paired difference;
- percentile-bootstrap 95% confidence interval of the mean difference, from 10,000 resamples of datasets;
- matched-pairs rank-biserial correlation;
- win/tie/loss counts.

**PhysioNet 2012.** Patients are the unit of analysis. We give a paired bootstrap (2,000 resamples) of the AUROC difference between seed-averaged score ensembles.

**Timing.** Wall-clock time was measured on a 4-core CPU with no GPU.

**Use of AI tools.** In line with the journal's policy, we document that an AI agent (Anthropic Claude) assisted with the literature search, the implementation of the code, experiment orchestration, analysis scripting and drafting. Every number in this paper is produced by the released code from the raw outputs, and every reference was verified against bibliographic databases (see Statements and Declarations).
