## 2 Related work

### 2.1 Random-convolution time series classification

ROCKET (Dempster et al. 2020) showed that thousands of random convolutional kernels, pooled by the proportion of positive values (PPV) and the maximum and followed by a linear classifier, rival far more expensive time series classifiers. MiniRocket (Dempster et al. 2021) replaced the random kernels by a small fixed set with weights in {−1, 2}, used PPV only, and became almost deterministic and up to two orders of magnitude faster. MultiRocket (Tan et al. 2022) added three pooling operators and a first-difference representation. Hydra (Dempster et al. 2023) turned the kernels into competing dictionary-like groups. QUANT (Dempster et al. 2024) showed that simple interval quantiles are similarly competitive. The bake-off of Middlehurst et al. (2024b) confirmed that convolution-based methods offer the best accuracy-to-cost ratio among recent algorithms, with only heavy meta-ensembles such as HIVE-COTE 2 (Middlehurst et al. 2021) more accurate.

All of these methods assume complete, equal-length input. Benchmark practice follows suit: the standard UCR evaluation uses the 112 or 113 datasets without missing values or unequal lengths (Bagnall et al. 2017; Middlehurst et al. 2024b), although the 2018 archive deliberately includes 15 incomplete or variable-length datasets (Dau et al. 2019). Where missing values must be handled, current studies zero-fill the series or pass NaNs through the transform to a learner that tolerates them. PYRREGULAR (Spinnato and Landi 2025) uses the latter approach, and in its benchmark of naturally irregular datasets MiniRocket nevertheless ranked first. To our knowledge, no previous work modifies the convolution response or the pooling of the ROCKET family to account for missingness.

### 2.2 Learning with missing values in time series

Deep missing-aware models encode the mask or time gaps inside a recurrent, attention or continuous-time architecture:
- GRU-D (Che et al. 2018), which decays inputs and hidden states toward empirical means;
- recurrent models with missingness indicators (Lipton et al. 2016);
- BRITS (Cao et al. 2018), with bidirectional recurrent imputation;
- multi-time attention networks (Shukla and Marlin 2021);
- set functions over observations (Horn et al. 2019);
- graph-guided networks for irregular multivariate series (Zhang et al. 2021);
- neural controlled differential equations (Kidger et al. 2020).

Other approaches impute first and then classify, using statistical, kernel-based or learned imputers. Examples include the time series cluster kernel (Mikalsen et al. 2018) and the self-attention imputer SAITS (Du et al. 2023). Closest to our setting, Yao et al. (2024) trained a GRU imputer jointly with a multi-scale convolutional classifier on 68 UCR datasets with simulated MCAR missingness, but compared only against deep models. Rhodes et al. (2025) proposed label-guided imputation using forest-based proximities, including proximities derived from ROCKET, and evaluated it on 85 UCR datasets under MCAR, MAR and MNAR with downstream random-forest and k-NN classifiers. Their method changes the imputer, not the transform.

### 2.3 Theory and practice of missing-value handling

For supervised prediction, Josse et al. (2019) and Le Morvan et al. (2021) showed that impute-then-predict can be Bayes-consistent for almost any imputation, provided the learner is flexible enough. Adding missingness indicators helps when missingness is informative (Lipton et al. 2016; Van Ness et al. 2023). Large benchmarks on health data found that native handling of missing values in tree ensembles, which goes back to approaches such as missing-incorporated-in-attributes (Twala et al. 2008), and indicator features often match or beat sophisticated imputation (Perez-Lebel et al. 2022).

These results assume flexible learners. ROCKET-family classifiers are instead *fixed* random-feature maps followed by a linear model, so how missingness enters the feature map matters directly. In image inpainting, partial convolutions renormalise each response by the fraction of observed inputs (Liu et al. 2018). Section 4.1 shows that this renormalisation breaks the zero-sum structure of MiniRocket kernels.

### 2.4 Gap addressed by this study

The literature therefore lacks:
- (i) a principled treatment of missingness inside random-convolution transforms;
- (ii) evidence on how imputation, native estimation, reliability weighting and indicator features compare for these classifiers across missingness mechanisms (MCAR, long gaps, value-dependent MNAR) and rates;
- (iii) an assessment of robustness to train–test missingness shift and on naturally incomplete data.

This study addresses all three under a pre-registered protocol with a separate development set.


## 3 Problem formulation and preliminaries

### 3.1 Classification with missing values

Let $\mathcal{D}=\{(\mathbf{x}_i,\mathbf{m}_i,y_i)\}_{i=1}^{n}$ be a training set of univariate series $\mathbf{x}_i\in\mathbb{R}^{L}$ with observation masks $\mathbf{m}_i\in\{0,1\}^{L}$ ($m_{it}=1$ if $x_{it}$ is observed) and labels $y_i\in\{1,\dots,K\}$. Values at positions with $m_{it}=0$ are unavailable. The task is to learn $f(\mathbf{x}\odot\mathbf{m},\mathbf{m})\mapsto y$. Variable-length series are represented by right-padding with unobserved positions. Following Rubin (1976), missingness is *missing completely at random* (MCAR) if $\mathbf{m}$ is independent of $(\mathbf{x},y)$, and *missing not at random* (MNAR) if it depends on the unobserved values themselves.

### 3.2 MiniRocket as a contrast of tap-group means

MiniRocket (Dempster et al. 2021) applies 84 fixed kernels of length nine. Each kernel is indexed by a set $P_k\subset\{0,\dots,8\}$ of three taps with weight $+2$; the remaining six taps $Q_k$ have weight $-1$. The kernels are applied at a set of dilations $d$. For position $t$ and dilation $d$, the tap values are $v_j(t)=x_{t+(j-4)d}$, with zero padding outside the series. The response is

$$C_k(t)=2\sum_{j\in P_k}v_j(t)-\sum_{j\in Q_k}v_j(t). \qquad (1)$$

Because the weights sum to zero ($3\cdot2-6\cdot1=0$), Eq. (1) can be rewritten as a scaled difference of two group means:

$$C_k(t)=6\big(\bar v_{P_k}(t)-\bar v_{Q_k}(t)\big),\qquad \bar v_{S}(t)=\tfrac{1}{|S|}\textstyle\sum_{j\in S}v_j(t). \qquad (2)$$

Each response is pooled by the *proportion of positive values* (PPV) with respect to a bias $b$. The biases are quantiles of the responses of a randomly chosen training series:

$$\mathrm{PPV}_{k,d,b}=\frac{1}{|T|}\sum_{t\in T}\mathbb{1}[C_k(t)>b]. \qquad (3)$$

Here $T$ is either all positions (zero padding) or the positions whose taps are all inside the series. MiniRocket alternates between the two choices across kernels and dilations. The roughly 10,000 resulting features are classified by a ridge classifier whose penalty is chosen by efficient leave-one-out (generalised) cross-validation.

Eq. (1) is undefined when taps are missing. The common practice is to fill the gaps first (zero, mean, last observation carried forward, or interpolation) and then apply Eq. (1) as if the series were complete.

## 4 Methods

### 4.1 A native estimator from observed taps

Equation (2) suggests estimating the response from the observed taps only. Let $O(t)$ be the set of observed taps; out-of-bounds taps under zero padding count as observed zeros, exactly as in MiniRocket. Let $n_P=|P_k\cap O(t)|$ and $n_Q=|Q_k\cap O(t)|$. Define

$$\hat C_k(t)=6\Big(\tfrac{1}{n_P}\textstyle\sum_{j\in P_k\cap O(t)}v_j(t)-\tfrac{1}{n_Q}\sum_{j\in Q_k\cap O(t)}v_j(t)\Big),\quad\text{defined if } n_P\ge1,\ n_Q\ge1. \qquad (4)$$

PPV is then computed over the positions where Eq. (4) is defined. We call this estimator *group-mean* (native) masking.

**Proposition 1 (properties of Eq. 4).**

\(i) *Exactness:* if $\mathbf{m}\equiv\mathbf{1}$, then $\hat C_k(t)=C_k(t)$ for all $k,t,d$.

\(ii) *Offset invariance:* for any constant $c$ and any window whose taps lie inside the series, $\hat C_k(t;\mathbf{x}+c\mathbf{1})=\hat C_k(t;\mathbf{x})$.

\(iii) *Conditional unbiasedness under MCAR:* if each tap is observed independently with the same probability, then $\mathbb{E}[\hat C_k(t)\mid n_P\ge1,n_Q\ge1]=C_k(t)$.

*Proof.*

\(i) With all taps observed, $n_P=3$ and $n_Q=6$, so Eq. (4) reduces to Eq. (2). In our implementation the coefficients $6/3$ and $6/6$ are exact in floating point, so the identity also holds bit-for-bit (unit test `test_complete_data_equivalence_responses`).

\(ii) Adding $c$ to every observed value adds $c$ to both observed-group means, and the difference is unchanged.

\(iii) Under MCAR and conditional on the counts, the observed subset of $P_k$ is a uniformly random subset of size $n_P$. The mean of a uniformly random subset is unbiased for the mean of the full set, and likewise for $Q_k$. Linearity completes the proof. ∎

By contrast, zero filling applies Eq. (1) to $\mathbf{x}\odot\mathbf{m}$. Its response to an offset $c$ changes by $c\,(2n_P-n_Q)$, which depends on the missingness pattern. Partial-convolution renormalisation (Liu et al. 2018) changes it by $9c\,(2n_P-n_Q)/(n_P+n_Q)$. Both therefore inject the level of the series into the response through the missingness pattern. Eq. (4) does not.

**Proposition 2 (variance).** Suppose $v_j=s_j+\varepsilon_j$, where $\varepsilon_j$ are i.i.d. with variance $\sigma^2$. Conditional on the observed set,

$$\mathrm{Var}[\hat C_k(t)\mid O]=36\sigma^2\big(1/n_P+1/n_Q\big).$$

This equals $18\sigma^2$ for complete windows and grows to $72\sigma^2$ when $n_P=n_Q=1$.

*Proof.* The two group means are independent, with variances $\sigma^2/n_P$ and $\sigma^2/n_Q$. ∎

Proposition 2 explains a central negative result of this study (Section 6). The native estimator is unbiased, but it discards the temporal smoothness that interpolation exploits. When gaps are short and scattered, which is typical of MCAR, an interpolated tap is a low-variance estimate of the missing value. A tap-wise unbiased estimate is noisier, and the noise propagates through the threshold in Eq. (3).

### 4.2 MissRocket: observed-tap-weighted pooling

Interpolation fails differently. Inside a long gap every tap is fabricated, and the response degenerates into a deterministic artefact of the interpolant.

**Proposition 3 (fabricated responses).** Let $\tilde{\mathbf{x}}$ be the linear interpolation of $\mathbf{x}$. If all nine taps of a window lie strictly inside one gap, so that $\tilde v_j=\alpha+\beta(j-4)d$, then

$$C_k(t)=\beta d\Big(2\sum_{j\in P_k}(j-4)-\sum_{j\in Q_k}(j-4)\Big).$$

This value depends only on the slope between the gap's two end points and on the kernel geometry, not on the unobserved signal.

*Proof.* Substitute the affine taps into Eq. (1). The constant $\alpha$ cancels because the weights sum to zero. ∎

Such windows are rare under MCAR. At a missing rate of $r$, the probability that all nine taps are missing is $r^9$, which is below 1% for $r=0.6$. They are common under contiguous (block) missingness, where they produce identical, spurious PPV contributions in every series with a gap of similar slope.

MissRocket keeps the low-variance interpolated responses but weights each position's contribution to PPV by the reliability of its window. Let $c(t)=|O(t)|\in\{0,\dots,9\}$ be the number of truly observed taps of the window at dilation $d$; padding taps count as observed, as above. With $w_\gamma(c)=(c/9)^\gamma$,

$$\mathrm{PPV}^{\gamma}_{k,d,b}=\frac{\sum_{t\in T}w_\gamma(c(t))\,\mathbb{1}[\tilde C_k(t)>b]}{\sum_{t\in T}w_\gamma(c(t))}, \qquad (5)$$

where $\tilde C_k$ is Eq. (1) evaluated on the linearly interpolated series. Positions with $c(t)=0$, which are exactly the fabricated windows of Proposition 3, receive zero weight for any $\gamma>0$. The exponent $\gamma$ interpolates between three cases:
- $\gamma=0$ gives MiniRocket on the interpolated series;
- $\gamma=1$ gives each window the fraction of its taps that were observed;
- $\gamma\to\infty$ keeps only completely observed windows.

We fixed $\gamma=1$ for the proposed method using the development datasets only (Section 5.4). The other values, and a variant that selects $\gamma$ on the training set, are reported as ablations.

**Proposition 4 (special cases).**
- If $\mathbf{m}\equiv\mathbf{1}$, MissRocket equals MiniRocket for every $\gamma$.
- For $\gamma=0$, MissRocket equals MiniRocket applied to the linearly interpolated series.

*Proof.* In the first case $c(t)=9$ and $w_\gamma=1$ everywhere, and $\tilde{\mathbf{x}}=\mathbf{x}$. In the second case $w_0\equiv1$. ∎

Biases are drawn as in MiniRocket, from the responses of a random training series at positions with $c(t)\ge1$. The classifier is MiniRocket's ridge head (standardisation followed by `RidgeClassifierCV` with $\alpha\in\{10^{-3},\dots,10^{3}\}$).

**Optional components (ablations).**
- *Missingness-pattern features:* MiniRocket applied to the binary mask, giving 1,000 features. This is a time-series analogue of the missing-indicator method (Van Ness et al. 2023).
- *Training-set selection:* $(\gamma,\text{mask})$ chosen from $\{0,0.5,1,2\}\times\{\text{off},\text{on}\}$ by the ridge head's leave-one-out criterion.
- *Other gap fillers:* zero, last observation carried forward (LOCF), and cross-series k-nearest-neighbour imputation.

### 4.3 Implementation and complexity

Because $w_\gamma$ depends only on the integer count $c(t)$, the numerator and denominator of Eq. (5) are obtained from per-count histograms of threshold exceedances. Several values of $\gamma$ can therefore be evaluated in one pass at negligible extra cost. Per series, the cost is that of MiniRocket, $\mathcal{O}(\sum_d L\,(84\cdot 9+F_d))$ with $F_d$ the number of features at dilation $d$, plus $\mathcal{O}(9L)$ per dilation to count observed taps. The implementation uses numba (Lam et al. 2015) and parallelises over series. The kernels, dilations, padding alternation and bias quantiles follow the reference MiniRocket code. On complete data our implementation reproduces the reference accuracy, and the proposed and standard responses agree bit-for-bit (unit tests).

For multivariate series (Section 5.3), the transform is applied channel-wise with a per-channel feature budget, and a single ridge head is fit on the concatenated features.


## 5 Experimental setup

### 5.1 Data

**UCR archive.** We use the 2018 UCR archive (Dau et al. 2019) with its fixed train/test splits. Of the 113 complete, equal-length datasets:
- 10 form a *development set* used for every design decision. These are the five datasets used for an initial feasibility pilot (ArrowHead, GunPoint, ECG200, Wafer, ShapesAll) plus five drawn at random with a fixed seed (CinCECGTorso, MoteStrain, MixedShapesSmallTrain, DistalPhalanxOutlineAgeGroup, MiddlePhalanxOutlineAgeGroup).
- The remaining 103 form the *confirmatory set*. A compute rule fixed before any confirmatory run (at most 2,000 training series and 2×10⁶ values in total) retains 91 of them. The excluded datasets are (test).

The 15 archive datasets with native missing values (4) or variable lengths (11) are used without simulation in Section 6.5. Variable-length series are represented by trailing missing values.

**PhysioNet/CinC 2012.** The challenge data (Goldberger et al. 2000; Silva et al. 2012) contain 12,000 intensive-care stays (sets a, b and c) with outcomes. We bin 37 time-varying variables into 48 hourly intervals; a bin with no measurement is missing. This gives 79.7% missing entries, missingness that is informative by nature, and 14.2% in-hospital mortality. Sets a and b (8,000 stays) are used for training and set c (4,000 stays) for testing. Variables are standardised with training statistics. Static descriptors are not used by any method.

### 5.2 Missingness simulation

Missingness is simulated independently for every series. Training and test masks are generated with different seeds, derived by hashing the dataset, mechanism, rate, seed and split, so every method sees exactly the same corrupted data. Three mechanisms are used:
- **MCAR:** each point is removed independently with probability $r$.
- **Block:** contiguous gaps of geometric length with mean 10% of the series length, placed uniformly until a fraction $r$ is removed. This models sensor dropout.
- **MNAR (self-masking):** $P(\text{missing})=\sigma(a+2z_t)$, where $z_t$ is the standardised value and $a$ is solved per series so that the expected fraction equals $r$. High values are preferentially lost, as with saturation.

We use $r\in\{0.2,0.5,0.8\}$ and keep at least two observed points per series. Unit tests verify the realised rates.

### 5.3 Methods compared

All ROCKET-family methods use the standard ridge head (standardisation followed by `RidgeClassifierCV`, $\alpha\in\{10^{-3},\dots,10^3\}$).

1. **Proposed: MissRocket.** Linear gap filling, MiniRocket kernels (10,000 features) and observed-tap-weighted PPV with $\gamma=1$ (Section 4.2).
2. **Imputation + reference MiniRocket.** The aeon implementation (Middlehurst et al. 2024a) after:
   - linear interpolation;
   - zero filling;
   - per-series mean filling;
   - LOCF;
   - cross-series k-nearest-neighbour imputation ($k=5$), fit on the training set.
3. **Stronger convolution classifiers after linear interpolation:** MultiRocket (Tan et al. 2022) and Hydra concatenated with MultiRocket (Dempster et al. 2023), both from aeon. These are among the most accurate convolution-based methods in the recent bake-off (Middlehurst et al. 2024b).
4. **Native estimator:** the group-mean MiniRocket of Section 4.1, which uses no imputation.
5. **Conventional ML with native missing-value handling:** LightGBM (Ke et al. 2017) on the raw time points (300 trees, learning rate 0.05, 31 leaves, `min_child_samples`=5, row and column subsampling).
6. **Classical baseline:** 1-NN with Euclidean distance after linear interpolation.
7. **Deep missing-aware baseline:** GRU-D (Che et al. 2018) with 64 hidden units, Adam (learning rate $10^{-3}$), early stopping on a stratified 20% validation split of the training data, and at most 60 epochs. On UCR it is run on a pre-registered subset (length ≤ 300, at most 500 training series; rate 0.5; seed 0) because of CPU cost. It is also run on PhysioNet 2012.

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
- the two-sided Wilcoxon signed-rank test (Wilcoxon 1945), with zero differences split, as recommended for comparing classifiers over multiple datasets (Benavoli et al. 2016; Demšar 2006);
- Holm's (1979) correction over the family of comparisons of MissRocket against all baselines within the condition.

**Effect sizes:**
- mean and median paired difference;
- percentile-bootstrap 95% confidence interval of the mean difference, from 10,000 resamples of datasets;
- matched-pairs rank-biserial correlation;
- win/tie/loss counts.

**PhysioNet 2012.** Patients are the unit of analysis. We give a paired bootstrap (2,000 resamples) of the AUROC difference between seed-averaged score ensembles.

**Timing.** Wall-clock time was measured on a 4-core CPU with no GPU.


## References

Bagnall A, Lines J, Bostrom A, Large J, Keogh E (2017) The great time series classification bake off: a review and experimental evaluation of recent algorithmic advances. Data Mining and Knowledge Discovery 31:606–660. https://doi.org/10.1007/s10618-016-0483-9

Benavoli A, Corani G, Mangili F (2016) Should we really use post-hoc tests based on mean-ranks? Journal of Machine Learning Research 17:1–10. https://jmlr.org/papers/v17/benavoli16a.html

Cao W, Wang D, Li J, Zhou H, Li L, Li Y (2018) BRITS: Bidirectional Recurrent Imputation for Time Series. arXiv:1805.10572. https://doi.org/10.48550/arXiv.1805.10572

Che Z, Purushotham S, Cho K, Sontag D, Liu Y (2018) Recurrent Neural Networks for Multivariate Time Series with Missing Values. Scientific Reports 8:6085. https://doi.org/10.1038/s41598-018-24271-9

Dau HA, Bagnall A, Kamgar K, Yeh CCM, Zhu Y, Gharghabi S, Ratanamahatana CA, Keogh E (2019) The UCR time series archive. IEEE/CAA Journal of Automatica Sinica 6:1293–1305. https://doi.org/10.1109/JAS.2019.1911747

Dempster A, Petitjean F, Webb GI (2020) ROCKET: exceptionally fast and accurate time series classification using random convolutional kernels. Data Mining and Knowledge Discovery 34:1454–1495. https://doi.org/10.1007/s10618-020-00701-z

Dempster A, Schmidt DF, Webb GI (2021) MiniRocket: A Very Fast (Almost) Deterministic Transform for Time Series Classification. In: Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery & Data Mining, pp 248–257. https://doi.org/10.1145/3447548.3467231

Dempster A, Schmidt DF, Webb GI (2023) Hydra: competing convolutional kernels for fast and accurate time series classification. Data Mining and Knowledge Discovery 37:1779–1805. https://doi.org/10.1007/s10618-023-00939-3

Dempster A, Schmidt DF, Webb GI (2024) quant: a minimalist interval method for time series classification. Data Mining and Knowledge Discovery 38:2377–2402. https://doi.org/10.1007/s10618-024-01036-9

Demšar J (2006) Statistical comparisons of classifiers over multiple data sets. Journal of Machine Learning Research 7:1–30. https://jmlr.org/papers/v7/demsar06a.html

Du W, Côté D, Liu Y (2023) SAITS: Self-attention-based imputation for time series. Expert Systems with Applications 219:119619. https://doi.org/10.1016/j.eswa.2023.119619

Goldberger AL, Amaral LAN, Glass L, Hausdorff JM, Ivanov PC, Mark RG, Mietus JE, Moody GB, Peng CK, Stanley HE (2000) PhysioBank, PhysioToolkit, and PhysioNet: Components of a New Research Resource for Complex Physiologic Signals. Circulation 101(23). https://doi.org/10.1161/01.CIR.101.23.e215

Horn M, Moor M, Bock C, Rieck B, Borgwardt K (2019) Set Functions for Time Series. arXiv:1909.12064. https://doi.org/10.48550/arXiv.1909.12064

Josse J, Chen JM, Prost N, Scornet E, Varoquaux G (2019) On the consistency of supervised learning with missing values. arXiv:1902.06931. https://doi.org/10.48550/arXiv.1902.06931

Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, Ye Q, Liu T-Y (2017) LightGBM: a highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30 (NIPS 2017). https://papers.nips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html

Kidger P, Morrill J, Foster J, Lyons T (2020) Neural Controlled Differential Equations for Irregular Time Series. arXiv:2005.08926. https://doi.org/10.48550/arXiv.2005.08926

Lam SK, Pitrou A, Seibert S (2015) Numba: a LLVM-based Python JIT compiler. In: Proceedings of the Second Workshop on the LLVM Compiler Infrastructure in HPC, pp 1–6. https://doi.org/10.1145/2833157.2833162

Le Morvan M, Josse J, Scornet E, Varoquaux G (2021) What's a good imputation to predict with missing values? arXiv:2106.00311. https://doi.org/10.48550/arXiv.2106.00311

Lipton ZC, Kale DC, Wetzel R (2016) Modeling Missing Data in Clinical Time Series with RNNs. arXiv:1606.04130. https://doi.org/10.48550/arXiv.1606.04130

Liu G, Reda FA, Shih KJ, Wang TC, Tao A, Catanzaro B (2018) Image Inpainting for Irregular Holes Using Partial Convolutions. In: Computer Vision – ECCV 2018, pp 89–105. https://doi.org/10.1007/978-3-030-01252-6_6

Middlehurst M, Ismail-Fawaz A, Guillaume A et al (2024a) aeon: a Python toolkit for learning from time series. Journal of Machine Learning Research 25:1–10. https://jmlr.org/papers/v25/23-1444.html

Middlehurst M, Large J, Flynn M, Lines J, Bostrom A, Bagnall A (2021) HIVE-COTE 2.0: a new meta ensemble for time series classification. Machine Learning 110:3211–3243. https://doi.org/10.1007/s10994-021-06057-9

Middlehurst M, Schäfer P, Bagnall A (2024b) Bake off redux: a review and experimental evaluation of recent time series classification algorithms. Data Mining and Knowledge Discovery 38:1958–2031. https://doi.org/10.1007/s10618-024-01022-1

Mikalsen KØ, Bianchi FM, Soguero-Ruiz C, Jenssen R (2018) Time series cluster kernel for learning similarities between multivariate time series with missing data. Pattern Recognition 76:569–581. https://doi.org/10.1016/j.patcog.2017.11.030

Perez-Lebel A, Varoquaux G, Le Morvan M, Josse J, Poline JB (2022) Benchmarking missing-values approaches for predictive models on health databases. GigaScience 11:giac013. https://doi.org/10.1093/gigascience/giac013

Rhodes JS, Rustad AG, Maia SP, Thacker E, Choi H, Gutierrez J, Rundek T, Shaw B (2025) Label-Guided Imputation via Forest-Based Proximities for Improved Time Series Classification. arXiv:2509.22919. https://doi.org/10.48550/arXiv.2509.22919

Rubin DB (1976) Inference and missing data. Biometrika 63:581–592. https://doi.org/10.1093/biomet/63.3.581

Shukla SN, Marlin BM (2021) Multi-Time Attention Networks for Irregularly Sampled Time Series. arXiv:2101.10318. https://doi.org/10.48550/arXiv.2101.10318

Silva I, Moody G, Scott DJ, Celi LA, Mark RG (2012) Predicting In-Hospital Mortality of ICU Patients: The PhysioNet/Computing in Cardiology Challenge 2012. Computing in Cardiology 39:245–248. PMID: 24678516

Spinnato F, Landi C (2025) PYRREGULAR: A Unified Framework for Irregular Time Series, with Classification Benchmarks. arXiv:2505.06047. https://doi.org/10.48550/arXiv.2505.06047

Tan CW, Dempster A, Bergmeir C, Webb GI (2022) MultiRocket: multiple pooling operators and transformations for fast and effective time series classification. Data Mining and Knowledge Discovery 36:1623–1646. https://doi.org/10.1007/s10618-022-00844-1

Twala B, Jones M, Hand D (2008) Good methods for coping with missing data in decision trees. Pattern Recognition Letters 29:950–956. https://doi.org/10.1016/j.patrec.2008.01.010

Van Ness M, Bosschieter TM, Halpin-Gregorio R, Udell M (2023) The Missing Indicator Method: From Low to High Dimensions. In: Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, pp 5004–5015. https://doi.org/10.1145/3580305.3599911

Wilcoxon F (1945) Individual Comparisons by Ranking Methods. Biometrics Bulletin 1:80. https://doi.org/10.2307/3001968

Yao P, Liu M, Cheng X, Shi F, Li H, Liu X, Chen S (2024) An End-to-End Model for Time Series Classification In the Presence of Missing Values. arXiv:2408.05849. https://doi.org/10.48550/arXiv.2408.05849

Zhang X, Zeman M, Tsiligkaridis T, Zitnik M (2021) Graph-Guided Network for Irregularly Sampled Multivariate Time Series. arXiv:2110.05357. https://doi.org/10.48550/arXiv.2110.05357
