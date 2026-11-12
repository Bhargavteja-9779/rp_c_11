# Missing values in random-convolution time series classification: observed-tap weighting for MiniRocket and a pre-specified evaluation

**Abstract**

Random-convolution classifiers such as MiniRocket are fast and accurate, but they assume complete series, so missing values are usually zero-filled or interpolated first. We analyse how missingness should enter these transforms. Writing MiniRocket's zero-sum kernel response as a contrast of tap-group means gives a native estimator that is unbiased under random missingness. It also shows that interpolation fabricates responses inside long gaps. We propose MissRocket, which keeps interpolated responses but weights each response's contribution to pooling by the fraction of its taps that were actually observed. In a pre-specified evaluation on 91 UCR datasets with three missingness mechanisms at three rates, MissRocket improved on MiniRocket with interpolation by +1.57 percentage points on average (Holm-adjusted Wilcoxon p < 0.001). The gain reached +4.46 points for contiguous gaps and +3.31 points for value-dependent missingness, with no significant difference under random missingness. It was markedly more robust when test data were more incomplete than training data. It matched MultiRocket and Hydra-MultiRocket on average at lower computational cost. However, the native estimator was consistently worse than interpolation. Cross-series k-nearest-neighbour imputation was more accurate on average for contiguous gaps. On sparse clinical records (PhysioNet 2012), GRU-D and gradient boosting outperformed all random-convolution methods. Code and per-run results are released.

**Keywords** Time series classification · Missing values · MiniRocket · Random convolutional kernels · Imputation · Robustness


## 1 Introduction

Time series classification (TSC) underpins applications such as industrial monitoring, wearable and clinical sensing, and remote sensing. In these settings the data are rarely complete. Sensors drop out for minutes or hours, communication links lose packets, values beyond an instrument's range are not recorded, and clinical variables are measured only when a clinician orders them. The resulting gaps differ in length, in how they relate to the signal, and in whether they carry information about the class.

Among accurate TSC methods, random-convolution transforms are the practical reference point. ROCKET (Dempster et al. 2020), MiniRocket (Dempster et al. 2021), MultiRocket (Tan et al. 2022) and Hydra (Dempster et al. 2023) are fast, and in a recent large benchmark Hydra combined with MultiRocket was, together with the far heavier HIVE-COTE 2, significantly more accurate than all other approaches (Middlehurst et al. 2024b). All of them, however, are defined for complete, equal-length input. In practice, missing values are therefore handled by ad-hoc preprocessing:

- the series is zero-filled or interpolated before the transform;
- or the incomplete datasets are simply excluded from benchmarks (Bagnall et al. 2017; Middlehurst et al. 2024b).

When NaNs are passed through such a transform, the downstream learner must cope with whatever the transform produces (Spinnato and Landi 2025). Deep missing-aware models exist (Che et al. 2018; Shukla and Marlin 2021; Yao et al. 2024; Zhang et al. 2021), but they are far costlier to train and tune, and they have rarely been compared with random-convolution pipelines under one protocol.

This leaves a practical and a scientific question open:

- *How should missingness enter a random-convolution transform?*
- Is imputation followed by the transform adequate?
- Should the transform estimate its kernel responses from the observed values only?
- Or should it treat responses that rely on missing data differently?

The answer is not obvious. Statistical theory shows that impute-then-predict is consistent when the learner is flexible enough (Josse et al. 2019; Le Morvan et al. 2021). Random-convolution classifiers, however, are fixed feature maps followed by a linear model, so the way missingness enters the feature map matters directly.

This paper studies the question for MiniRocket, the simplest and fastest member of the family.

- **The kernel response as a contrast of means.** The zero-sum MiniRocket kernel response is a scaled difference of two tap-group means (Section 3.2). This yields a native estimator from observed taps that is exact on complete data, invariant to the series level, and unbiased under MCAR. It also shows why renormalised (partial) convolutions are ill-suited to these kernels.
- **Interpolation fails in a specific way.** Interpolation produces low-variance but *fabricated* responses inside long gaps (Proposition 3). This motivates **MissRocket**: interpolated responses are retained, but each response's contribution to the proportion-of-positive-values pooling is weighted by the fraction of its taps that were actually observed.
- **The method adds no learnable parameters.** It reduces exactly to MiniRocket on complete data and has the same asymptotic cost.

Our contributions are:

1. An analysis, based on elementary but consequential observations, of missingness inside MiniRocket kernels: exactness, offset invariance, unbiasedness and the variance of a native estimator; the failure of partial-convolution renormalisation; and the fabricated-response property of interpolation (Section 4).
2. **MissRocket**, an observed-tap-weighted pooling scheme that requires no imputation model and no training beyond the usual ridge head (Section 4.2).
3. A pre-specified evaluation with a separate development set. It covers 91 UCR datasets, three missingness mechanisms (MCAR, contiguous gaps and value-dependent MNAR) at three rates, and eleven competitors, including reference MiniRocket, MultiRocket and Hydra with five imputation strategies, LightGBM with native missing-value handling, and GRU-D. It also includes ablations, train–test missingness shift, 15 naturally incomplete UCR datasets and PhysioNet 2012 mortality prediction (Sections 5–6).
4. Empirical evidence on where each strategy succeeds and fails:
   - observed-tap weighting helps substantially when gaps are long, when missingness depends on the values, and under train–test missingness shift;
   - it neither helps nor materially hurts under scattered random gaps;
   - native estimation is consistently inferior to interpolation;
   - cross-series kNN imputation and clinical-specific models are better in their respective niches (Sections 6–7).

All code, raw per-run results and the scripts that generate every number, table and figure are released.


## 2 Related work

### 2.1 Random-convolution time series classification

ROCKET (Dempster et al. 2020) showed that thousands of random convolutional kernels, pooled by the proportion of positive values (PPV) and the maximum and followed by a linear classifier, rival far more expensive time series classifiers. MiniRocket (Dempster et al. 2021) replaced the random kernels by a small fixed set with weights in {−1, 2}, used PPV only, and became almost deterministic and up to 75 times faster on larger datasets. MultiRocket (Tan et al. 2022) added three pooling operators and a first-difference representation. Hydra (Dempster et al. 2023) organises random kernels into competing groups and counts which kernel in each group matches best. QUANT (Dempster et al. 2024) showed that simple interval quantiles are similarly competitive. The bake-off of Middlehurst et al. (2024b) found Hydra combined with MultiRocket, together with the meta-ensemble HIVE-COTE 2 (Middlehurst et al. 2021), to be significantly more accurate than all other approaches.

All of these methods assume complete, equal-length input. Benchmark practice follows suit: the standard UCR evaluation uses the 112 or 113 datasets without missing values or unequal lengths (Bagnall et al. 2017; Middlehurst et al. 2024b), although the 2018 archive deliberately includes 15 incomplete or variable-length datasets (Dau et al. 2019). Where missing values must be handled, current studies zero-fill the series or pass NaNs through the transform to a learner that tolerates them. PYRREGULAR (Spinnato and Landi 2025) uses the latter approach, and in its benchmark of naturally irregular datasets MiniRocket nevertheless ranked first. To our knowledge, no previous work modifies the convolution response or the pooling of the ROCKET family to account for missingness. This conclusion rests on web and arXiv searches carried out in November 2026, combining ROCKET, MiniRocket, MultiRocket, Hydra and QUANT with missing values, NaN, masks, masked or partial convolution, imputation and irregular series, and on reading the closest works in full.

### 2.2 Learning with missing values in time series

Deep learning for complete series is reviewed by Ismail Fawaz et al. (2019). Deep missing-aware models encode the mask or time gaps inside a recurrent, attention or continuous-time architecture:

- GRU-D (Che et al. 2018), which decays inputs and hidden states toward empirical means;
- recurrent models with missingness indicators (Lipton et al. 2016);
- BRITS (Cao et al. 2018), with bidirectional recurrent imputation;
- multi-time attention networks (Shukla and Marlin 2021);
- set functions over observations (Horn et al. 2019);
- graph-guided networks for irregular multivariate series (Zhang et al. 2021);
- neural controlled differential equations (Kidger et al. 2020).

Other approaches impute first and then classify, using statistical, kernel-based or learned imputers. Examples include the time series cluster kernel (Mikalsen et al. 2018) and the self-attention imputer SAITS (Du et al. 2023). Kim et al. (2023) instead train a probabilistic imputer jointly with the classifier. Closest to our setting, Yao et al. (2024) trained a GRU imputer jointly with a multi-scale convolutional classifier on 68 UCR datasets with simulated MCAR missingness; their comparisons do not include ROCKET-family methods. Rhodes et al. (2025) proposed label-guided imputation using forest-based proximities, including proximities derived from ROCKET, and evaluated it on 85 UCR datasets under MCAR, MAR and MNAR with downstream random-forest and k-NN classifiers. Their method changes the imputer, not the transform.

### 2.3 Theory and practice of missing-value handling

For supervised prediction, Josse et al. (2019) and Le Morvan et al. (2021) showed that impute-then-predict can be Bayes-consistent for almost any imputation, provided the learner is flexible enough. Adding missingness indicators helps when missingness is informative (Lipton et al. 2016; Van Ness et al. 2023). Large benchmarks on health data found that native handling of missing values in tree ensembles, which goes back to approaches such as missing-incorporated-in-attributes (Twala et al. 2008), and indicator features often match or beat sophisticated imputation (Perez-Lebel et al. 2022).

These results assume flexible learners. ROCKET-family classifiers are instead *fixed* random-feature maps followed by a linear model, so how missingness enters the feature map matters directly. In image inpainting, partial convolutions renormalise each response by the fraction of observed inputs (Liu et al. 2018). Section 4.1 shows that this renormalisation breaks the zero-sum structure of MiniRocket kernels.

### 2.4 Gap addressed by this study

The literature therefore lacks:

- (i) a principled treatment of missingness inside random-convolution transforms;
- (ii) evidence on how imputation, native estimation, reliability weighting and indicator features compare for these classifiers across missingness mechanisms (MCAR, long gaps, value-dependent MNAR) and rates;
- (iii) an assessment of robustness to train–test missingness shift and on naturally incomplete data.

This study addresses all three under a pre-specified protocol with a separate development set.


## 3 Problem formulation and preliminaries

### 3.1 Classification with missing values

Let $\mathcal{D}=\{(\mathbf{x}_i,\mathbf{m}_i,y_i)\}_{i=1}^{n}$ be a training set of univariate series $\mathbf{x}_i\in\mathbb{R}^{L}$ with observation masks $\mathbf{m}_i\in\{0,1\}^{L}$ ($m_{it}=1$ if $x_{it}$ is observed) and labels $y_i\in\{1,\dots,K\}$. Values at positions with $m_{it}=0$ are unavailable. The task is to learn $f(\mathbf{x}\odot\mathbf{m},\mathbf{m})\mapsto y$. Variable-length series are represented by right-padding with unobserved positions. Following Rubin (1976) and Little and Rubin (2019), missingness is *missing completely at random* (MCAR) if $\mathbf{m}$ is independent of $(\mathbf{x},y)$, and *missing not at random* (MNAR) if it depends on the unobserved values themselves.

### 3.2 MiniRocket as a contrast of tap-group means

MiniRocket (Dempster et al. 2021) applies 84 fixed kernels of length nine. Each kernel is indexed by a set $P_k\subset\{0,\dots,8\}$ of three taps with weight $+2$; the remaining six taps $Q_k$ have weight $-1$. The kernels are applied at a set of dilations $d$. For position $t$ and dilation $d$, the tap values are $v_j(t)=x_{t+(j-4)d}$, with zero padding outside the series. The response is

$$C_k(t)=2\sum_{j\in P_k}v_j(t)-\sum_{j\in Q_k}v_j(t) \qquad (1)$$

Because the weights sum to zero ($3\cdot2-6\cdot1=0$), Eq. (1) can be rewritten as a scaled difference of two group means:

$$C_k(t)=6\big(\bar v_{P_k}(t)-\bar v_{Q_k}(t)\big),\qquad \bar v_{S}(t)=\tfrac{1}{|S|}\textstyle\sum_{j\in S}v_j(t) \qquad (2)$$

Each response is pooled by the *proportion of positive values* (PPV) with respect to a bias $b$. The biases are quantiles of the responses of a randomly chosen training series:

$$\mathrm{PPV}_{k,d,b}=\frac{1}{|T|}\sum_{t\in T}\mathbb{1}[C_k(t)>b] \qquad (3)$$

Here $T$ is either all positions (zero padding) or the positions whose taps are all inside the series. MiniRocket alternates between the two choices across kernels and dilations. The roughly 10,000 resulting features are classified by a ridge classifier whose penalty is chosen by efficient leave-one-out (generalised) cross-validation.

Eq. (1) is undefined when taps are missing. The common practice is to fill the gaps first (zero, mean, last observation carried forward, or interpolation) and then apply Eq. (1) as if the series were complete.

## 4 Methods

### 4.1 A native estimator from observed taps

Equation (2) suggests estimating the response from the observed taps only. Let $O(t)$ be the set of observed taps; out-of-bounds taps under zero padding count as observed zeros, exactly as in MiniRocket. Let $n_P=|P_k\cap O(t)|$ and $n_Q=|Q_k\cap O(t)|$. Define

$$\hat C_k(t)=6\Big(\tfrac{1}{n_P}\textstyle\sum_{j\in P_k\cap O(t)}v_j(t)-\tfrac{1}{n_Q}\sum_{j\in Q_k\cap O(t)}v_j(t)\Big),\quad\text{defined if } n_P\ge1,\ n_Q\ge1 \qquad (4)$$

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

These results are elementary, but they are consequential. Proposition 2 explains a central negative result of this study (Section 6). The native estimator is unbiased, but it discards the temporal smoothness that interpolation exploits. When gaps are short and scattered, which is typical of MCAR, an interpolated tap is a low-variance estimate of the missing value. A tap-wise unbiased estimate is noisier, and the noise propagates through the threshold in Eq. (3).

### 4.2 MissRocket: observed-tap-weighted pooling

Interpolation fails differently. Inside a long gap every tap is fabricated, and the response degenerates into a deterministic artefact of the interpolant.

**Proposition 3 (fabricated responses).** Let $\tilde{\mathbf{x}}$ be the linear interpolation of $\mathbf{x}$. If all nine taps of a window lie strictly inside one gap, so that $\tilde v_j=\alpha+\beta(j-4)d$, then

$$C_k(t)=\beta d\Big(2\sum_{j\in P_k}(j-4)-\sum_{j\in Q_k}(j-4)\Big).$$

This value depends only on the slope between the gap's two end points and on the kernel geometry, not on the unobserved signal.

*Proof.* Substitute the affine taps into Eq. (1). The constant $\alpha$ cancels because the weights sum to zero. ∎

Such windows are rare under MCAR. At a missing rate of $r$, the probability that all nine taps are missing is $r^9$, which is below 1% for $r=0.6$. They are common under contiguous (block) missingness, where they produce identical, spurious PPV contributions in every series with a gap of similar slope.

MissRocket keeps the low-variance interpolated responses but weights each position's contribution to PPV by the reliability of its window. Let $c(t)=|O(t)|\in\{0,\dots,9\}$ be the number of truly observed taps of the window at dilation $d$; padding taps count as observed, as above. With $w_\gamma(c)=(c/9)^\gamma$,

$$\mathrm{PPV}^{\gamma}_{k,d,b}=\frac{\sum_{t\in T}w_\gamma(c(t))\,\mathbb{1}[\tilde C_k(t)>b]}{\sum_{t\in T}w_\gamma(c(t))} \qquad (5)$$

where $\tilde C_k$ is Eq. (1) evaluated on the linearly interpolated series. Missing values before the first or after the last observation take the nearest observed value. As in MiniRocket, taps beyond the ends of the series under zero padding count as observed zeros, which preserves exact equivalence with MiniRocket on complete data. Positions with $c(t)=0$, which are exactly the fabricated windows of Proposition 3, receive zero weight for any $\gamma>0$. The exponent $\gamma$ interpolates between three cases:

- $\gamma=0$ gives MiniRocket on the interpolated series;
- $\gamma=1$ gives each window the fraction of its taps that were observed;
- $\gamma\to\infty$ keeps only completely observed windows.

Fig. 1 summarises the pipeline. Fig. 2 illustrates it on a real series.

![](../code/results/full/figures/Fig1_pipeline.png){width=16.5cm}

**Fig. 1** MissRocket pipeline. The only differences from MiniRocket are the gap filling of the input and the use of the observation mask to weight each response in the proportion-of-positive-values pooling

![](../code/results/full/figures/Fig2_worked_example.png){width=16cm}

**Fig. 2** Worked example computed with the released code on a development-set series (GunPoint, first training series, 40% block missingness). **a** Observed points and linear interpolation. **b** Response of one MiniRocket kernel (dilation 1) on the complete and on the interpolated series. Red points mark windows with no observed tap (c = 0), where the interpolated response is constant within each gap, as stated by Proposition 3. **c** The observed-tap weight c/9 used by MissRocket (γ = 1), which is zero exactly on those windows

We fixed $\gamma=1$ for the proposed method using the development datasets only (Section 5.4). The other values, and a variant that selects $\gamma$ on the training set, are reported as ablations.

**Relation to masked pooling and partial convolution.** Excluding invalid positions from pooling is a familiar idea. Sequence models routinely average only over non-padded positions, and partial convolutions renormalise each response by the fraction of valid inputs (Liu et al. 2018). Observed-tap weighting differs from both in three respects:
- (i) the weights are fractional reliabilities of whole windows, computed per dilation from the original mask, rather than binary validity flags;
- (ii) they enter a thresholded pooling (PPV), not an average;
- (iii) the response itself is computed on the gap-filled series and left unchanged, which keeps the low variance of interpolation.

The two alternatives correspond to variants we evaluated. Partial-convolution renormalisation changes the response value (Section 4.1) and was the least accurate of the four response estimators on the development set (Online Resource 1). Binary support pooling combined with responses estimated from observed taps is the native estimator, which was significantly less accurate than MissRocket in every confirmatory condition (Section 6.1).

**Proposition 4 (special cases).**

- If $\mathbf{m}\equiv\mathbf{1}$, MissRocket equals MiniRocket for every $\gamma$.
- For $\gamma=0$, MissRocket equals MiniRocket applied to the linearly interpolated series.

*Proof.* In the first case $c(t)=9$ and $w_\gamma=1$ everywhere, and $\tilde{\mathbf{x}}=\mathbf{x}$. In the second case $w_0\equiv1$. ∎

Biases are drawn as in MiniRocket, from the responses of a random training series at positions with $c(t)\ge1$. The classifier is MiniRocket's ridge head (standardisation followed by `RidgeClassifierCV` with $\alpha\in\{10^{-3},\dots,10^{3}\}$).

**Optional components (ablations).**

- *Missingness-pattern features:* MiniRocket applied to the binary mask, with a budget of 1,000 features (924 after rounding to whole multiples of the 84 kernels). This is a time-series analogue of the missing-indicator method (Van Ness et al. 2023).
- *Training-set selection:* $(\gamma,\text{mask})$ chosen from $\{0,0.5,1,2\}\times\{\text{off},\text{on}\}$ by the ridge head's leave-one-out criterion.
- *Other gap fillers:* zero, last observation carried forward (LOCF), and cross-series k-nearest-neighbour imputation.

### 4.3 Implementation and complexity

Because $w_\gamma$ depends only on the integer count $c(t)$, the numerator and denominator of Eq. (5) are obtained from per-count histograms of threshold exceedances. Several values of $\gamma$ can therefore be evaluated in one pass at negligible extra cost. Per series, the cost is that of MiniRocket, $\mathcal{O}(\sum_d L\,(84\cdot 9+F_d))$ with $F_d$ the number of features at dilation $d$, plus $\mathcal{O}(9L)$ per dilation to count observed taps. The implementation uses numba (Lam et al. 2015) and parallelises over series. The kernels, dilations, padding alternation and bias quantiles follow the reference MiniRocket code. On complete data our implementation reproduces the reference accuracy, and the proposed and standard responses agree bit-for-bit (unit tests).

For multivariate series (Section 5.3), the transform is applied channel-wise with a per-channel feature budget, and a single ridge head is fit on the concatenated features.


## 5 Experimental setup

### 5.1 Data

**UCR archive.** We use the 2018 UCR archive (Dau et al. 2019) with its fixed train/test splits. Of the 113 complete, equal-length datasets:

- 10 form a *development set* used for every design decision. These are the five datasets used for an initial feasibility pilot (ArrowHead, GunPoint, ECG200, Wafer, ShapesAll) plus five drawn at random with a fixed seed (CinCECGTorso, MoteStrain, MixedShapesSmallTrain, DistalPhalanxOutlineAgeGroup, MiddlePhalanxOutlineAgeGroup).
- The remaining 103 form the *confirmatory set*. A compute rule fixed before any confirmatory run (at most 2,000 training series and 2×10⁶ values in total) retains 91 of them. The excluded datasets are Crop, ElectricDevices, FordA, FordB, HandOutlines, Mallat, MixedShapesRegularTrain, NonInvasiveFetalECGThorax1, NonInvasiveFetalECGThorax2, Phoneme, StarLightCurves, UWaveGestureLibraryAll.

The 15 archive datasets with native missing values (4) or variable lengths (11) are used without simulation in Section 6.5. Variable-length series are represented by trailing missing values.

**PhysioNet/CinC 2012.** The challenge data (Goldberger et al. 2000; Silva et al. 2012) contain 12,000 intensive-care stays (sets a, b and c) with outcomes. We bin 37 time-varying variables into 48 hourly intervals; a bin with no measurement is missing. This gives 79.7% missing entries, missingness that is informative by nature, and 14.2% in-hospital mortality. Sets a and b (8,000 stays) are used for training and set c (4,000 stays) for testing. Variables are standardised with training statistics. Static descriptors are not used by any method.

### 5.2 Missingness simulation

Missingness is simulated independently for every series. Training and test masks are generated with different seeds, derived by hashing the dataset, mechanism, rate, seed and split, so every method sees exactly the same corrupted data. Three mechanisms are used:

- **MCAR:** each point is removed independently with probability $r$.
- **Block:** contiguous gaps of geometric length with mean 10% of the series length, placed uniformly until a fraction $r$ is removed. This models sensor dropout.
- **MNAR (self-masking):** $P(\text{missing})=\sigma(a+2z_t)$, where $z_t$ is the standardised value and $a$ is solved per series so that the expected fraction equals $r$. High values are preferentially lost, as with saturation.

We use $r\in\{0.2,0.5,0.8\}$ and keep at least two observed points per series. Unit tests verify the realised rates.

### 5.3 Methods compared

All ROCKET-family methods use the standard ridge head (standardisation followed by `RidgeClassifierCV` from scikit-learn (Pedregosa et al. 2011), $\alpha\in\{10^{-3},\dots,10^3\}$).

1. **Proposed: MissRocket.** Linear gap filling, MiniRocket kernels (10,000 features) and observed-tap-weighted PPV with $\gamma=1$ (Section 4.2).
2. **Imputation + reference MiniRocket.** The aeon implementation (Middlehurst et al. 2024a) after:
   - linear interpolation;
   - zero filling;
   - per-series mean filling;
   - LOCF;
   - cross-series k-nearest-neighbour imputation ($k=5$), fit on the training set.
3. **Stronger convolution classifiers after linear interpolation:** MultiRocket (Tan et al. 2022) and Hydra concatenated with MultiRocket (Dempster et al. 2023), both from aeon. These are among the most accurate convolution-based methods in the recent bake-off (Middlehurst et al. 2024b).
4. **Native estimator:** the group-mean MiniRocket of Section 4.1, which uses no imputation.
5. **Conventional ML with native missing-value handling:** LightGBM (Ke et al. 2017) on the raw time points (300 trees, learning rate 0.05, 31 leaves, `min_child_samples`=5, row subsampling 0.8, column subsampling 0.5). On PhysioNet 2012, with 8,000 training stays, we used 500 trees, learning rate 0.03 and `min_child_samples`=20.
6. **Classical baseline:** 1-NN with Euclidean distance after linear interpolation.
7. **Deep missing-aware baseline:** GRU-D (Che et al. 2018) with 64 hidden units, Adam (learning rate $10^{-3}$), early stopping (patience 8 epochs, restoring the best weights) on a stratified 20% validation split of the training data, and at most 60 epochs. On UCR it is run on a pre-specified subset (length ≤ 300, at most 500 training series; rate 0.5; seed 0) because of CPU cost. It is also run on PhysioNet 2012.

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
   - the primary benchmark E1 uses seed 0 on all 91 eligible datasets;
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

- the two-sided Wilcoxon signed-rank test (Wilcoxon 1945), with zero differences split, as recommended for comparing classifiers over multiple datasets (Benavoli et al. 2016; Demšar 2006);
- Holm's step-down correction (Holm 1979) over the family of comparisons of MissRocket against all baselines within the condition.

**Effect sizes:**

- mean and median paired difference;
- percentile-bootstrap 95% confidence interval of the mean difference, from 10,000 resamples of datasets;
- matched-pairs rank-biserial correlation;
- win/tie/loss counts.

**Multiplicity.** Each mechanism–rate condition is treated as a separate, pre-specified question, and Holm's correction controls the family-wise error rate within a condition only. The pooled comparison over all nine conditions serves as the single overall test. Per-condition p-values describe where an effect appears and should not be read as nine independent confirmations.

**PhysioNet 2012.** Patients are the unit of analysis. We give a paired bootstrap (2,000 resamples) of the AUROC difference between seed-averaged score ensembles.

**Timing.** Wall-clock time was measured on a 4-core CPU with no GPU.

**Use of AI tools.** In line with the journal's policy, we document that an AI agent (Anthropic Claude) assisted with the literature search, the implementation of the code, experiment orchestration, analysis scripting and drafting. Every number in this paper is produced by the released code from the raw outputs, and every reference was verified against bibliographic databases (see Statements and Declarations).


## 6 Results

### 6.1 Main comparison (RQ1)

Table 1 reports mean test accuracy over the 91 confirmatory datasets for every mechanism and rate. Paired comparisons with the strongest competitors are given in Table 2, and pooled comparisons in Table 3. Fig. 3 shows accuracy against the missing rate.

**Table 1** Mean test accuracy over 91 UCR datasets (seed 0) under MCAR, block (contiguous-gap) and MNAR (self-masking) missingness at 20%, 50% and 80% missing values. Columns: C, B and N denote MCAR, block and MNAR missingness; the number is the missing rate in %. Mean rank is computed among the eleven methods of the main comparison (the γ=0 ablation is excluded). Best value per column in bold

| Method | C20 | C50 | C80 | B20 | B50 | B80 | N20 | N50 | N80 | Mean | Mean rank |
|:------------------------------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| MissRocket (proposed) | 0.850 | 0.824 | **0.744** | 0.791 | 0.691 | 0.561 | **0.834** | **0.790** | **0.698** | **0.754** | 3.70 |
| Hydra-MultiRocket + linear interp. | **0.854** | 0.830 | 0.737 | 0.794 | 0.674 | 0.533 | 0.832 | 0.782 | 0.675 | 0.746 | 3.88 |
| MultiRocket + linear interp. | 0.852 | 0.827 | 0.739 | 0.793 | 0.667 | 0.532 | 0.830 | 0.780 | 0.679 | 0.744 | 4.05 |
| w/o weighting (γ=0) | 0.853 | **0.831** | 0.743 | 0.785 | 0.662 | 0.534 | 0.830 | 0.776 | 0.669 | 0.743 | – |
| MiniRocket + linear interp. | 0.853 | 0.830 | 0.741 | 0.781 | 0.652 | 0.516 | 0.830 | 0.775 | 0.665 | 0.738 | 4.61 |
| MiniRocket + kNN impute | 0.835 | 0.778 | 0.661 | **0.810** | **0.722** | **0.566** | 0.819 | 0.747 | 0.633 | 0.730 | 5.04 |
| MiniRocket + LOCF | 0.842 | 0.806 | 0.701 | 0.766 | 0.632 | 0.499 | 0.823 | 0.763 | 0.643 | 0.719 | 5.63 |
| Native masked MiniRocket (group-mean) | 0.810 | 0.739 | 0.626 | 0.750 | 0.643 | 0.525 | 0.803 | 0.754 | 0.665 | 0.702 | 6.19 |
| MiniRocket + zero fill | 0.773 | 0.698 | 0.582 | 0.747 | 0.628 | 0.505 | 0.783 | 0.715 | 0.633 | 0.674 | 7.30 |
| MiniRocket + mean fill | 0.772 | 0.691 | 0.563 | 0.743 | 0.605 | 0.476 | 0.775 | 0.699 | 0.610 | 0.660 | 8.03 |
| LightGBM (native NaN) | 0.682 | 0.613 | 0.501 | 0.666 | 0.593 | 0.500 | 0.681 | 0.636 | 0.551 | 0.603 | 8.22 |
| 1-NN ED + linear interp. | 0.682 | 0.659 | 0.592 | 0.615 | 0.523 | 0.429 | 0.662 | 0.606 | 0.531 | 0.589 | 9.35 |


Averaged over the nine conditions, MissRocket attains the highest mean accuracy and the best mean rank. The differences are condition-specific, however.

**Long gaps.** Under block missingness, MissRocket improves on MiniRocket with linear interpolation at every rate:

- 20%: +1.08 pp;
- 50%: +3.94 pp;
- 80%: +4.46 pp;

all with Holm-adjusted p ≤ 0.002.

At 50% and 80%, MissRocket is also significantly more accurate than MultiRocket and Hydra-MultiRocket after interpolation. Both are considerably more expensive transforms; Section 6.6 gives the costs.

**Value-dependent missingness.** Under MNAR, the gains over MiniRocket with interpolation grow with the missing rate:

- 20%: +0.42 pp, p (Holm) = 0.557;
- 50%: +1.56 pp, p (Holm) = 0.002;
- 80%: +3.31 pp, p (Holm) < 0.001.

**Scattered gaps.** Under MCAR, MissRocket is not significantly different from MiniRocket with interpolation at any rate: the mean differences are -0.36, -0.58 and +0.31 pp. At 20% MCAR it is slightly but significantly *less* accurate than MultiRocket (-0.24 pp, p (Holm) = 0.012) and than Hydra-MultiRocket (-0.42 pp, p (Holm) = 0.012).

**Table 2** Paired comparison of MissRocket with the strongest competitors and with its own unweighted ablation (γ=0) per condition (C, B, N: MCAR, block, MNAR at the given rate in %): mean accuracy difference in percentage points over the 91 datasets (positive favours MissRocket) and, in parentheses, the two-sided Wilcoxon signed-rank p-value, Holm-corrected within each condition over the ten baselines (γ=0: separate single comparison). Bootstrap 95% CIs, win/tie/loss counts and rank-biserial correlations for all comparisons are given in Online Resource 1

| MissRocket vs. | C20 | C50 | C80 | B20 | B50 | B80 | N20 | N50 | N80 |
|:--------------------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| MiniRocket + linear interp. | -0.36 (0.328) | -0.58 (0.330) | +0.31 (0.257) | +1.08 (0.002) | +3.94 (<0.001) | +4.46 (<0.001) | +0.42 (0.557) | +1.56 (0.002) | +3.31 (<0.001) |
| w/o weighting (γ=0) | -0.38 (0.324) | -0.68 (0.014) | +0.11 (0.466) | +0.67 (0.013) | +2.98 (<0.001) | +2.64 (<0.001) | +0.37 (0.823) | +1.41 (0.001) | +2.90 (<0.001) |
| MultiRocket + linear interp. | -0.24 (0.012) | -0.33 (0.330) | +0.60 (0.257) | -0.12 (0.219) | +2.40 (<0.001) | +2.81 (<0.001) | +0.39 (0.497) | +1.04 (1.000) | +1.95 (0.017) |
| Hydra-MultiRocket + linear interp. | -0.42 (0.012) | -0.61 (0.330) | +0.76 (0.200) | -0.29 (0.164) | +1.74 (0.019) | +2.79 (<0.001) | +0.20 (0.387) | +0.80 (1.000) | +2.31 (0.007) |
| MiniRocket + kNN impute | +1.46 (0.001) | +4.54 (<0.001) | +8.36 (<0.001) | -1.82 (0.219) | -3.02 (0.040) | -0.52 (0.997) | +1.45 (<0.001) | +4.30 (<0.001) | +6.56 (<0.001) |


**Cross-series kNN imputation.** kNN imputation followed by MiniRocket behaves very differently by mechanism. It is the most accurate method under block missingness. At 50% blocks it is 3.02 pp better than MissRocket (p (Holm) = 0.040). Under MCAR and MNAR, by contrast, it is substantially worse; at 80% MCAR, MissRocket is +8.36 pp better. Exploiting aligned training series therefore pays off when whole segments are missing, but it is harmful when the gaps are short and scattered.

**Native estimation and generic learners.**

- The native group-mean estimator is significantly worse than MissRocket in every condition. This confirms, on held-out data, the development-set observation and Proposition 2: an unbiased but high-variance response estimate loses to interpolation.
- LightGBM with native missing-value handling, and 1-NN after interpolation, are far less accurate than every ROCKET-family pipeline.
- Zero and mean filling are the worst gap fillers for MiniRocket. This matters because zero filling is common in practice.

**Table 3** Pooled comparison over all nine conditions (per-dataset mean accuracy over conditions; 91 datasets)

| Baseline | Δ acc. (pp) [95% CI] | W/T/L | r_rb | p (Holm) |
|:------------------------------|----------:|----------:|----------:|----------:|
| MiniRocket + linear interp. | +1.57 [+1.18, +1.99] | 78/2/11 | +0.84 | <0.001 |
| MiniRocket + zero fill | +8.01 [+6.56, +9.52] | 83/1/7 | +0.94 | <0.001 |
| MiniRocket + mean fill | +9.42 [+7.92, +10.99] | 87/1/3 | +0.99 | <0.001 |
| MiniRocket + LOCF | +3.44 [+2.75, +4.18] | 79/1/11 | +0.93 | <0.001 |
| MiniRocket + kNN impute | +2.37 [+0.69, +4.05] | 62/1/28 | +0.44 | <0.001 |
| MultiRocket + linear interp. | +0.95 [+0.22, +1.81] | 53/2/36 | +0.24 | 0.103 |
| Hydra-MultiRocket + linear interp. | +0.81 [+0.18, +1.53] | 48/1/42 | +0.15 | 0.210 |
| Native masked MiniRocket (group-mean) | +5.20 [+4.04, +6.41] | 82/0/9 | +0.90 | <0.001 |
| LightGBM (native NaN) | +15.12 [+11.82, +18.68] | 73/0/18 | +0.87 | <0.001 |
| 1-NN ED + linear interp. | +16.49 [+13.97, +19.35] | 87/1/3 | +0.99 | <0.001 |
| w/o weighting (γ=0) | +1.11 [+0.79, +1.45] | 77/1/13 | +0.77 | <0.001 |


Pooled over all conditions, MissRocket is more accurate than MiniRocket with interpolation by +1.57 pp (95% CI +1.18 to +1.99; 78 wins and 11 losses; p (Holm) < 0.001).

The pooled differences from MultiRocket (+0.95 pp, p (Holm) = 0.103) and from Hydra-MultiRocket (+0.81 pp, p (Holm) = 0.210) are not statistically significant. We therefore do not claim that MissRocket outperforms these stronger transforms overall. What the data show is that observed-tap weighting lets the cheapest member of the family match them on average, and beat them when gaps are long or missingness depends on the values.

![](../code/results/full/figures/Fig_accuracy_vs_rate.png){width=16.5cm}

**Fig. 3** Mean accuracy over 91 datasets as a function of the missing rate for each mechanism (seed 0)

![](../code/results/full/figures/Fig_paired_differences.png){width=16.5cm}

**Fig. 4** Distribution over datasets of the accuracy difference between MissRocket and MiniRocket with linear interpolation (percentage points). Boxes show quartiles, whiskers 1.5 IQR, points outliers

### 6.2 Ablation study (RQ2–RQ3)

The ablations were run on a pre-declared random subset of 30 confirmatory datasets, at rate 0.5, for each mechanism (seed 0). Table 4 compares MissRocket with each variant. Table 5 isolates the effect of weighting for each gap filler.

**Table 4** Ablations on 30 datasets at 50% missing values. "acc." is the mean accuracy of the variant; Δ is MissRocket minus the variant in percentage points (positive favours MissRocket), with the Holm-corrected Wilcoxon p-value (family: the twelve comparisons within a mechanism)

| Variant (vs. MissRocket) | MCAR: acc. | MCAR: Δ (pp), p | Block: acc. | Block: Δ (pp), p | MNAR: acc. | MNAR: Δ (pp), p |
|:------------------------------|----------:|----------:|----------:|----------:|----------:|----------:|
| MissRocket (γ=1, linear filling) | 0.806 | – | 0.693 | – | 0.784 | – |
| w/o weighting (γ=0) | 0.813 | -0.67, 0.394 | 0.659 | +3.41, 0.001 | 0.766 | +1.72, 1.000 |
| γ=0.5 | 0.813 | -0.71, 0.394 | 0.694 | -0.11, 0.805 | 0.782 | +0.20, 1.000 |
| γ=2 | 0.799 | +0.67, 0.068 | 0.689 | +0.44, 0.368 | 0.782 | +0.14, 1.000 |
| + mask-pattern features | 0.799 | +0.64, 0.019 | 0.688 | +0.53, 0.453 | 0.787 | -0.32, 1.000 |
| γ, mask selected by LOO | 0.810 | -0.43, 1.000 | 0.684 | +0.87, 0.453 | 0.784 | -0.08, 0.670 |
| LOCF gap filling, γ=1 | 0.787 | +1.84, 0.049 | 0.672 | +2.11, 0.013 | 0.771 | +1.30, 0.165 |
| zero gap filling, γ=1 | 0.691 | +11.50, <0.001 | 0.648 | +4.52, 0.001 | 0.713 | +7.02, <0.001 |
| kNN gap filling, γ=1 | 0.764 | +4.17, 0.040 | 0.721 | -2.82, 0.238 | 0.745 | +3.90, 0.083 |


**Table 5** Effect of observed-tap weighting (γ=1 vs γ=0) for each gap filler on the same 30 datasets at 50% missing values: mean difference in pp (W/T/L; Holm-corrected p over the twelve filler × mechanism comparisons)

| Gap filler | MCAR | Block | MNAR |
|:------------------------------|----------:|----------:|----------:|
| linear | -0.67 (8/2/20; p 0.782) | +3.41 (26/1/3; p 0.001) | +1.72 (16/3/11; p 1.000) |
| LOCF | -0.83 (10/9/11; p 1.000) | +2.15 (25/2/3; p 0.001) | +0.62 (18/2/10; p 1.000) |
| zero | +0.41 (21/3/6; p 0.243) | +1.50 (20/2/8; p 0.218) | +1.34 (16/3/11; p 1.000) |
| kNN | +0.16 (18/3/9; p 0.782) | -0.62 (18/1/11; p 0.972) | +1.39 (14/3/13; p 1.000) |


**Weighting is the active component.** Removing it (γ=0) costs 3.41 pp under block missingness (p (Holm) = 0.001), with 26 of 30 datasets improving. On all 91 datasets and rates the effect is consistent (Table 2):

- weighting improves on γ=0 under block missingness at every rate, and under MNAR at 50% and 80%;
- it is neutral under MCAR, except for a small significant loss at 50% (-0.68 pp, p (Holm) = 0.014).

**The benefit is not tied to linear interpolation.** Weighting also improves LOCF filling under block missingness (Table 5). It does *not* improve kNN filling, which does not draw straight lines through gaps and therefore does not produce the fabricated responses of Proposition 3.

**Statistical power.** With 30 datasets and Holm correction over twelve comparisons, non-significant differences in this subset are inconclusive rather than evidence of no effect. The comparison with γ=0 on all 91 datasets (Table 2) is the primary evidence for the effect of weighting.

**The exponent is not critical.** γ=0.5 and γ=2 are not significantly different from γ=1 in any mechanism. Selecting γ and the mask option on the training set by leave-one-out brings no significant improvement either. This is consistent with the development-set observation that motivated fixing γ=1.

**Missingness-pattern features do not help.** Adding them to MissRocket gives no significant gain under block or MNAR missingness. Under MCAR they are slightly harmful (+0.64 pp in favour of MissRocket without them, p (Holm) = 0.019), where the mask is pure noise.

**The gap filler matters.** Zero filling is far worse than linear filling even with weighting. kNN filling is the strongest filler under block missingness but loses under MCAR and MNAR, mirroring the main comparison.

### 6.3 Robustness to train–test missingness shift (RQ4)

In deployment, a classifier is often trained on curated, complete data and then applied to series with gaps. It may also be trained on data with modest gaps and then face much heavier ones. Table 6 reports three such shifts, on the 30-dataset subset (seed 0).

**Table 6** Accuracy under train–test missing-rate shift (30 datasets). Baseline cells: accuracy (MissRocket minus baseline in pp; W/T/L; Holm-corrected p within the shift condition)

| Mechanism | Train → test rate | MissRocket | MiniRocket + interp. | Native masked | LightGBM |
|:------------------------------|----------:|----------:|----------:|----------:|----------:|
| Block | 0% → 50% | 0.616 | 0.493 (+12.3; 24/3/3; p <0.001) | 0.510 (+10.7; 28/0/2; p <0.001) | 0.497 (+11.9; 21/0/9; p 0.010) |
| Block | 0% → 80% | 0.463 | 0.374 (+8.9; 26/0/4; p <0.001) | 0.390 (+7.2; 23/0/7; p <0.001) | 0.390 (+7.3; 20/0/10; p 0.022) |
| Block | 20% → 80% | 0.512 | 0.407 (+10.5; 28/0/2; p <0.001) | 0.468 (+4.4; 22/2/6; p 0.022) | 0.466 (+4.5; 19/1/10; p 0.233) |
| MCAR | 0% → 50% | 0.754 | 0.773 (-1.9; 11/6/13; p 0.313) | 0.456 (+29.8; 29/1/0; p <0.001) | 0.519 (+23.5; 26/1/3; p <0.001) |
| MCAR | 0% → 80% | 0.633 | 0.621 (+1.2; 16/2/12; p 0.133) | 0.363 (+27.0; 27/1/2; p <0.001) | 0.378 (+25.4; 24/0/6; p <0.001) |
| MCAR | 20% → 80% | 0.654 | 0.639 (+1.5; 16/6/8; p 0.038) | 0.464 (+19.1; 24/1/5; p <0.001) | 0.471 (+18.3; 19/0/11; p 0.012) |


**Block missingness.** Here the shift is most harmful, and MissRocket is markedly more robust. Trained on complete data and tested with 50% block missingness, it reaches 0.616, against 0.493 for MiniRocket with interpolation (p (Holm) < 0.001).

This holds even though the training data contain no missing values, and the reason is the test-time weighting. When the model is trained on complete series, all weights equal one during training. At test time, the weighting removes the fabricated responses inside long gaps, so the pooled features stay closer to the distribution seen in training.

**MCAR.** The shift has little effect on either interpolation-based method. Differences are small: -1.91 pp for 0%→50% (not significant) and +1.53 pp for 20%→80% (p (Holm) = 0.038).

**Mechanism shift.** The missingness *mechanism* may also change between training and deployment, for example from sporadic dropouts to long outages. We added this experiment in response to an internal review (it was not part of the pre-specified protocol). It uses the same 30 datasets, 50% missing values and seed 0 (Table 7).

**Table 7** Accuracy under train–test mechanism shift (30 datasets, 50% missing values, seed 0). Baseline cells: accuracy (MissRocket minus baseline in pp; W/T/L; Holm-corrected p within the shift condition). Added post hoc

| Method | Train MCAR → test block | Train block → test MCAR |
|:--------------------|----------:|----------:|
| MissRocket | 0.647 | 0.729 |
| w/o weighting (γ=0) | 0.531 (+11.7; 26/1/3; p <0.001) | 0.656 (+7.4; 22/0/8; p 0.011) |
| MiniRocket + linear interp. | 0.525 (+12.2; 24/3/3; p <0.001) | 0.654 (+7.5; 22/0/8; p 0.007) |
| MiniRocket + kNN impute | 0.677 (-2.9; 11/0/19; p 0.560) | 0.661 (+6.9; 18/1/11; p 0.092) |
| Native masked MiniRocket | 0.546 (+10.1; 24/0/6; p <0.001) | 0.566 (+16.3; 22/2/6; p <0.001) |
| LightGBM (native NaN) | 0.599 (+4.8; 19/0/11; p 0.560) | 0.620 (+10.9; 18/1/11; p 0.023) |


The concern that weighting might hurt when the training data have different gaps than the test data is not borne out. MissRocket was the most robust interpolation-based method in both directions:
- *MCAR → block:* +12.21 pp over MiniRocket with interpolation, p (Holm) < 0.001;
- *block → MCAR:* +7.50 pp, p (Holm) = 0.007.

In the second direction the gain arises because training on block-missing data without weighting teaches the classifier fabricated responses, which do not occur at test time. Under MCAR → block shift, kNN imputation was again slightly more accurate than MissRocket (not significant).

**Native estimators under shift.** The native group-mean estimator and LightGBM degrade severely under MCAR shift. Both rely on statistics whose distribution changes with the missing rate.

### 6.4 External validation: PhysioNet 2012 mortality prediction (RQ5)

**Table 8** In-hospital mortality prediction on PhysioNet/CinC 2012 (37 hourly variables over 48 h, 79.7% missing). Train: sets a+b (8,000 stays). Test: set c (4,000 stays). Seed 0. ROCKET-family methods are applied channel-wise (252 features per channel). Time is wall clock for training and prediction on 4 CPU cores

| Method | AUROC | AUPRC | Time (s) |
|:------------------------------|----------:|----------:|----------:|
| GRU-D | 0.860 | 0.540 | 1148 |
| LightGBM (native NaN) | 0.846 | 0.522 | 12 |
| γ, mask selected by LOO | 0.806 | 0.491 | 373 |
| w/o weighting (γ=0) | 0.806 | 0.491 | 65 |
| MissRocket (proposed) | 0.803 | 0.489 | 66 |
| Native masked MiniRocket (group-mean) | 0.785 | 0.451 | 53 |


**Table 9** Paired bootstrap (2,000 resamples of test patients) of the AUROC difference between MissRocket and each method; p < 0.001 means that no resample produced a difference of the opposite sign

| Method | ΔAUROC (MissRocket − method) | 95% CI | Bootstrap p |
|:------------------------------|----------:|----------:|----------:|
| w/o weighting (γ=0) | -0.003 | [-0.016, +0.008] | 0.540 |
| γ, mask selected by LOO | -0.003 | [-0.016, +0.008] | 0.540 |
| Native masked MiniRocket (group-mean) | +0.018 | [-0.001, +0.037] | 0.068 |
| LightGBM (native NaN) | -0.043 | [-0.060, -0.026] | <0.001 |
| GRU-D | -0.057 | [-0.074, -0.042] | <0.001 |


PhysioNet 2012 differs from the UCR experiments in four ways: the series are multivariate, short (48 hourly bins) and very sparse, and their missingness is informative by nature. The results (Table 8, Table 9) are a clear *negative* finding for the random-convolution family.

- **No gain from weighting.** MissRocket (AUROC 0.803) does not improve on its unweighted counterpart (AUROC 0.806). Training-set selection chooses γ=0 without mask features.
- **The deep missing-aware model is best.** GRU-D, which models the mask and the time since the last observation explicitly, attains the highest AUROC (0.860) and AUPRC (0.540). Its training takes about 1148 s, against 66 s for MissRocket.
- **Gradient boosting comes second.** LightGBM on the raw hourly values with native missing-value handling follows (AUROC 0.846).
- **Both beat MissRocket significantly.** The AUROC difference between MissRocket and GRU-D is -0.057 (95% CI -0.074 to -0.042). Against LightGBM it is -0.043 (95% CI -0.060 to -0.026).

The test-set bootstrap captures uncertainty from patient sampling, not from training stochasticity (for example GRU-D's initialisation), since each method was trained once. ROC and precision–recall curves are given in Online Resource 1.

We attribute the gap to the nature of the data:

- whether, and when, a laboratory value was measured carries information about patient severity;
- the measured *levels* matter more than local temporal shape;
- many channel–patient series are entirely empty.

Models that see the mask and the measured levels directly can exploit each of these; GRU-D does so through its decay mechanism and tree ensembles through their native handling of missing values. Kernels designed to detect shape cannot. Observed-tap weighting addresses fabricated responses inside interpolated gaps, and it cannot add the missingness-pattern and level information that this task needs. We therefore regard MissRocket as suited to *shape-based* classification of sensor-like series with gaps, not as a general method for sparse, irregular clinical records.

### 6.5 Naturally incomplete and variable-length data (RQ5)

**Table 10** Accuracy (mean over three seeds) on the 15 UCR datasets that contain native missing values (DodgerLoop*, MelbournePedestrian) or series of unequal length (all others). Variable-length series are right-padded with missing values; "resampling" stretches each series to the common length before MiniRocket (the MiniRocket implementation in aeon 1.6 does not support unequal lengths natively; its documented options are padding, truncation or resizing)

| Dataset | MissRocket (proposed) | w/o weighting (γ=0) | MiniRocket + linear interp. | MiniRocket + resampling | Native masked MiniRocket (group-mean) | LightGBM (native NaN) | 1-NN ED + linear interp. |
|:------------------------------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| AllGestureWiimoteX | 0.742 | 0.753 | 0.709 | 0.711 | **0.780** | 0.507 | 0.461 |
| AllGestureWiimoteY | 0.789 | 0.783 | 0.761 | 0.744 | **0.796** | 0.569 | 0.496 |
| AllGestureWiimoteZ | **0.739** | 0.701 | 0.671 | 0.712 | 0.729 | 0.491 | 0.443 |
| DodgerLoopDay | **0.696** | 0.662 | 0.662 | 0.662 | 0.646 | 0.583 | 0.588 |
| DodgerLoopGame | 0.865 | 0.867 | 0.870 | 0.870 | 0.850 | 0.734 | **0.884** |
| DodgerLoopWeekend | 0.978 | **0.986** | **0.986** | **0.986** | 0.947 | 0.908 | **0.986** |
| GestureMidAirD1 | 0.751 | 0.715 | 0.718 | 0.700 | **0.764** | 0.567 | 0.462 |
| GestureMidAirD2 | 0.636 | 0.623 | 0.636 | 0.590 | **0.682** | 0.459 | 0.400 |
| GestureMidAirD3 | 0.436 | 0.449 | 0.400 | 0.462 | **0.469** | 0.331 | 0.208 |
| GesturePebbleZ1 | 0.897 | 0.901 | 0.886 | **1.000** | 0.922 | 0.793 | 0.535 |
| GesturePebbleZ2 | 0.861 | 0.816 | 0.823 | **0.890** | 0.869 | 0.747 | 0.494 |
| MelbournePedestrian | 0.962 | 0.962 | 0.966 | 0.966 | 0.962 | **0.969** | 0.945 |
| PLAID | 0.935 | 0.891 | 0.880 | 0.915 | **0.951** | 0.778 | 0.655 |
| PickupGestureWiimoteZ | 0.827 | 0.787 | 0.780 | **0.860** | 0.847 | 0.687 | 0.620 |
| ShakeGestureWiimoteZ | **0.920** | 0.907 | 0.840 | 0.900 | 0.900 | 0.713 | 0.520 |
| Mean | 0.802 | 0.787 | 0.772 | 0.798 | **0.808** | 0.656 | 0.580 |


Table 10 reports the 15 archive datasets that are incomplete by nature, analysed without any simulated missingness. MissRocket is more accurate than MiniRocket with linear interpolation, by +2.98 pp (11 wins, 3 losses; p (Holm) = 0.016).

For variable-length series, interpolation extends the last observed value over the padded tail. This creates exactly the fabricated, constant windows of Proposition 3, and MissRocket gives them zero weight.

MissRocket is not significantly different from two alternatives:

- the standard resampling approach (+0.44 pp, p (Holm) = 0.820);
- the native group-mean estimator (-0.53 pp, p (Holm) = 0.820).

The native estimator is competitive here because the missing segment is a single trailing block rather than many interior gaps.

On the four datasets with genuinely missing interior values (DodgerLoopDay, DodgerLoopGame, DodgerLoopWeekend and MelbournePedestrian), the missing fraction is below 1% and all ROCKET-family methods perform similarly. With 15 datasets, these comparisons have limited power.

### 6.6 Computational cost (RQ6)

**Table 11** Wall-clock cost per run (fit + predict, including gap filling) on a 4-core CPU without GPU, over all E1 runs (seed 0, nine conditions, 91 datasets). Our MiniRocket implementation (MissRocket, γ=0) is a numba re-implementation; "MiniRocket + …" rows use the optimised reference implementation in aeon

| Method | Median time per run (s) | Relative to MiniRocket+interp. | Total wall time, 9 conditions (h) | Features |
|:------------------------------|----------:|----------:|----------:|----------:|
| 1-NN ED + linear interp. | 0.01 | 0.0× | 0.00 | 301 |
| MiniRocket + linear interp. | 0.30 | 1.0× | 0.10 | 9,996 |
| MiniRocket + kNN impute | 0.50 | 1.7× | 0.22 | 9,996 |
| Native masked MiniRocket (group-mean) | 0.54 | 1.8× | 0.23 | 9,996 |
| LightGBM (native NaN) | 0.69 | 2.3× | 0.52 | 301 |
| MissRocket (proposed) | 1.24 | 4.1× | 0.60 | 9,996 |
| w/o weighting (γ=0) | 1.25 | 4.1× | 0.58 | 9,996 |
| MultiRocket + linear interp. | 2.56 | 8.4× | 0.93 | 49,728 |
| Hydra-MultiRocket + linear interp. | 4.11 | 13.5× | 1.96 | 55,872 |


Table 11 summarises the measured costs.

**The weighting is essentially free.** MissRocket and its unweighted counterpart (γ=0) have practically identical run times. The only additions are a per-position count of observed taps and a ten-bin histogram per feature (Section 4.3).

**Implementation, not method, explains the gap to aeon.** Both of our variants are about 4.1× slower than the reference aeon MiniRocket. This reflects the difference between our straightforward numba implementation and aeon's heavily optimised one, not the method; the transform has the same asymptotic cost as MiniRocket.

**Cheaper than the stronger transforms.** Even with this implementation gap, MissRocket is about 3.3× faster than Hydra-MultiRocket and uses fewer than a fifth of its features. At the same time, it is at least as accurate on average (Section 6.1).

**Controlled scaling benchmark.** To separate method from implementation we ran a controlled benchmark of the transform alone. It used synthetic random-walk series with 50% block missingness, measured each configuration in an isolated process on an otherwise idle machine, and took the median of three repeats after a warm-up (Online Resource 1, Fig. S13).
- *Weighting is free:* at n = 1,000 series of length 2,048, MissRocket took 13.2 s and its γ=0 variant 13.2 s.
- *Implementation gap:* aeon's MiniRocket took 1.0 s. Our transform is thus an order of magnitude slower than the optimised reference implementation; with the classifier included, the gap shrinks to the factor of about four in Table 11.
- *Stronger transforms:* MultiRocket took 12.4 s and Hydra-MultiRocket 46.4 s.
- *Memory:* the peak resident memory of MissRocket (373 MB) was the lowest of all methods. Hydra-MultiRocket needed 8284 MB.
- *Scaling:* all methods scaled approximately linearly in the number and length of the series.

**Model-based imputation adds cost and memory.** kNN imputation must store the training set and compare every test series with it. Its cost grows with the size of the training set, whereas MissRocket processes each series independently.

GRU-D, which needs iterative training with early stopping, is compared in Sections 6.4 and 6.9.

### 6.7 Sensitivity analysis

Fig. 5 shows how MissRocket responds to the weighting exponent and to the feature budget. The evaluation uses 30 confirmatory datasets drawn with a fixed seed, at 50% block and MCAR missingness.

**Weighting exponent γ.**

- *Block missingness:* every γ between 0.25 and 2 is clearly better than γ=0 (0.642). The curve peaks at γ=0.5 (0.679), against 0.673 for the pre-specified γ=1.
- *MCAR:* accuracy is flat up to γ=0.5 (0.805 at γ=0, 0.805 at γ=0.5). It then declines slowly (0.799 at γ=1) and sharply at γ=4 (0.764). At γ=4 the pooling effectively discards every window that contains a single missing tap.
- *Interpretation:* γ=0.5 would have been a marginally better choice than γ=1 on these data. Because γ=1 was fixed on the development set before the confirmatory runs, we keep it as the reported method and note γ≈0.5 as a recommendation for practitioners. The effect sizes involved are small compared with the effect of using any γ>0 under long gaps.

**Feature budget.** Between 2,500 and 20,000 features, the accuracy of both MissRocket and its unweighted counterpart changes little. The block-missingness gain of weighting is stable across budgets, as is the small MCAR difference. The conclusions therefore do not depend on the default budget of 10,000 features.

![](../code/results/full/figures/Fig_sensitivity.png){width=16cm}

**Fig. 5** Sensitivity of MissRocket on 30 datasets at 50% missing values: (left) weighting exponent γ (γ=0 is MiniRocket on the interpolated series; dotted line: the pre-specified γ=1); (right) number of features, for γ=1 (solid) and γ=0 (dashed)

### 6.8 Error analysis

**Overall distribution.** Averaged over the nine conditions, MissRocket is more accurate than MiniRocket with interpolation on 86% of the 91 datasets and less accurate on 12%. The largest average losses are small: Wine (-3.5 pp), SmallKitchenAppliances (-1.5 pp), EOGVerticalSignal (-1.4 pp). The largest average gains are much larger: PigCVP (+10.0 pp), OliveOil (+7.8 pp), PigArtPressure (+7.5 pp).

**When the method helps.** Across conditions, the pattern is clear. The gain is large under block missingness, grows with the missing rate under block and MNAR missingness, and is absent under MCAR (Table 1, Table 2). Within a condition, dataset properties explain little of the variation across datasets. We computed Spearman correlations separately for each mechanism and rate, so that each dataset contributes one point (n = 91), with Holm correction within each mechanism.

The only significant associations occur at 80% block missingness. There the gain increases with series length (ρ = 0.35, Holm-adjusted p = 0.013) and with the absolute mean gap length (ρ = 0.34, p = 0.015). It decreases with the gap length *relative* to the series length (ρ = -0.36, p = 0.007). This is consistent with the gain arising when gaps are long compared with the kernel windows, while enough of the series remains observed. Signal roughness is not associated with the gain in any condition.

![](../code/results/full/figures/Fig_error_gain_vs_gap.png){width=16.5cm}

**Fig. 6** Per-dataset gain of MissRocket over MiniRocket with linear interpolation (percentage points) against the realised mean gap length relative to the series length, by mechanism and rate (seed 0; one point per dataset and rate). The vertical spread within a rate is much larger than any trend

**Failure cases.** The largest single-condition losses all occur on datasets with small test sets, mostly smooth spectrograms: OliveOil (MCAR 50%, -23.3 pp); Wine (MCAR 20%, -18.5 pp); Wine (MCAR 50%, -14.8 pp); OliveOil (MCAR 20%, -13.3 pp); Herring (MCAR 80%, -10.9 pp); Coffee (Block 80%, -10.7 pp). Their test-set sizes are OliveOil: 30, Wine: 54, Herring: 64, Coffee: 28, so one misclassified series changes accuracy by 1.6–3.6 pp. For such smooth signals with short, scattered gaps, linear interpolation is nearly exact, and down-weighting those windows discards accurate information. With so few test series these differences are also very noisy. OliveOil, for example, shows the worst single-condition loss and yet one of the largest average gains. Section 6.9 reports variability across seeds.

**Confusion matrices.** Fig. 7 shows the confusion matrices for the largest loss and the largest gain at 50% block missingness.

- *Largest loss:* HouseTwenty, accuracy 0.790 vs 0.882. The loss comes from reduced recall on one of the two classes.
- *Largest gain:* PigCVP, a 52-class dataset, accuracy 0.793 vs 0.462. The improvement is spread over many classes. This is consistent with interpolated gaps making series from different classes look alike, through identical straight segments, and with the weighting removing that confound.

![](../code/results/full/figures/Fig_confusion_extremes.png){width=15cm}

**Fig. 7** Confusion matrices at 50% block missingness (seed 0) for the dataset with the largest loss (top) and the largest gain (bottom) of MissRocket (left) relative to MiniRocket with linear interpolation (right)

### 6.9 Deep missing-aware baseline on UCR and variability across seeds

**GRU-D on UCR.** Because of its CPU cost, GRU-D was run on the eligible datasets with series length ≤ 200 and at most 300 training series (17 datasets; 50% missing values; seed 0). In this small-data regime it was far less accurate than both random-convolution pipelines. Its mean accuracy was 0.544 under block missingness, against 0.837 for MissRocket. MissRocket was more accurate on 17, 16 and 17 of the datasets under MCAR, block and MNAR missingness, respectively (Online Resource 1). The median GRU-D run took about 30 times longer than a MissRocket run (13.8 s vs 0.45 s). With at most 300 training series and default settings, a recurrent model is at a disadvantage. The result shows that GRU-D is not competitive at the scale of these UCR datasets; it is not evidence against GRU-D in general, and GRU-D was the best model on PhysioNet 2012 (Section 6.4). On the same subset, MissRocket again improved on MiniRocket with interpolation under block missingness (+2.38 pp) and MNAR (+2.19 pp), and was on par under MCAR (-0.03 pp).

**Variability across seeds.** On the 30-dataset subset, run with seeds 0, 1 and 2, we computed the mean difference between MissRocket and each baseline separately for each seed. Its sign agreed across all three seeds in 95% of the 99 condition–baseline combinations. The combinations without agreement were Block 80% vs MiniRocket + kNN impute; MCAR 80% vs MiniRocket + linear interp; MCAR 80% vs MultiRocket + linear interp; MCAR 80% vs w/o weighting (γ=0); MNAR 20% vs MultiRocket + linear interp. In all of them the mean difference stayed within ±1.3 pp, that is, close to zero. For the two key comparisons, with MiniRocket and interpolation and with the γ=0 ablation, the sign agreed in 89% of the condition–baseline combinations. The median standard deviation over seeds of the mean difference was 0.40 pp. Under block missingness at 50% and 80%, the gain over MiniRocket with interpolation ranged from +4.16 to +5.29 pp across seeds. Every effect reported as significant in Section 6.1 has the same sign in every seed; only differences that are already near zero change sign (Online Resource 1, Table S5).


## 7 Discussion

### 7.1 What the evidence supports

The experiments answer the motivating question in a nuanced but consistent way.

**First, native estimation from observed taps loses to interpolation.** The group-mean estimator is principled: it is exact on complete data, invariant to the level of the series, and unbiased under MCAR (Proposition 1). Yet it was significantly less accurate than MissRocket in every one of the nine confirmatory conditions, and in most conditions less accurate than plain interpolation as well. Proposition 2 explains why. Estimating a response from one or two taps per group inflates its variance up to fourfold. Interpolation, in contrast, exploits the smoothness of the signal to produce low-variance tap values whenever gaps are short. For random-convolution features, which are thresholded and pooled, variance appears to matter more than bias. We regard this negative result as useful: it rules out the most natural "missingness-aware" modification of the transform.

**Second, interpolation fails in a specific, identifiable way, and the failure can be repaired cheaply.** Inside a long gap, an interpolated window carries no information about the signal (Proposition 3); its response depends only on the slope between the gap's two end points. Weighting each response by the fraction of its taps that were observed removes these windows from the pooled statistics. Several results show that this is the operative mechanism:

- the gain over unweighted interpolation is large under contiguous gaps and under value-dependent MNAR, where missing values cluster, and absent under scattered MCAR gaps;
- the gain grows with the missing rate under block and MNAR missingness, although dataset properties, gap length among them, explain little of the variation across datasets within a condition (Section 6.8);
- weighting also repairs LOCF filling, which produces fabricated *constant* segments;
- weighting does not improve kNN filling, which does not create such segments.

**Consistency with earlier benchmarks.** These findings are consistent with the observation that unadapted MiniRocket ranked first on naturally irregular datasets (Spinnato and Landi 2025). MiniRocket with interpolation is a strong pipeline, and our natural-data results show it close to the best (Section 6.5). The gains from weighting concentrate where gaps are long.

**Third, robustness to train–test shift.** The robustness under train–test shift (Section 6.3) is, in our view, the most practically relevant result. A model trained on complete data and deployed on series with long gaps loses heavily with interpolation, and much less with observed-tap weighting.

### 7.2 What the evidence does not support

We do not claim that MissRocket is the best approach to classification with missing values in general.

- **Stronger transforms.** Pooled over all conditions, its advantage over MultiRocket and Hydra-MultiRocket is not statistically significant. Under 20% MCAR it is slightly worse than both.
- **kNN imputation.** Cross-series kNN imputation is clearly better under contiguous gaps. In such settings the aligned training series contain more information about a missing segment than its two end points. The combination of kNN filling and weighting did not help (Table 5). The two approaches are complementary rather than nested, and choosing between them per dataset is an open question. Training-set selection by leave-one-out was not reliable in our ablation.
- **Sparse clinical records.** On PhysioNet 2012, both a deep missing-aware model (GRU-D) and gradient boosting with native missing-value handling were significantly better than every random-convolution method, MissRocket included. Shape-based kernels are poorly matched to very sparse, short, multivariate records in which the *presence* and *level* of measurements carry the signal.

### 7.3 Practical recommendations

Our evidence supports the following guidance for practitioners using ROCKET-family classifiers on incomplete series:

- Avoid zero and mean filling; they were the worst gap fillers in every condition.
- Use linear interpolation together with observed-tap weighting (γ between 0.5 and 1). This costs essentially nothing over MiniRocket and is never much worse than interpolation alone. It helps substantially when gaps are long, when missingness depends on the values, or when test data may be more incomplete than training data.
- If gaps are long and the training series are well aligned, try kNN imputation.
- For sparse multivariate clinical records, prefer models that use the measurement pattern directly.
- For deployment, MissRocket processes each series independently, needs no training data at prediction time (unlike kNN imputation), and has the latency of MiniRocket.

### 7.4 Limitations

1. **Seeds.** Infrastructure constraints (Section 5.4) limited the primary benchmark to one seed per dataset. Variability across seeds was assessed only on a 30-dataset subset (Section 6.9). The dataset, not the seed, is the unit of our statistical analysis, so additional seeds would mainly reduce within-dataset noise. That noise is substantial for datasets with very small test sets (Section 6.8).
2. **Dataset coverage.** The pre-specified compute rule excluded the 12 largest confirmatory datasets. The ablation and shift experiments use a 30-dataset subset at a single rate.
3. **Simulated missingness.** Our mechanisms (MCAR, geometric blocks with a mean length of 10% of the series, logistic self-masking) are idealisations, and the gap length was not varied systematically. Within conditions, the realised gap length was only weakly associated with the gain (Section 6.8). No dataset in our benchmark has long *interior* gaps that arose naturally, so the long-gap results rest on simulation. The UCR series were z-normalised before values were removed, whereas in practice normalisation would use the observed values only. MissRocket's responses are offset-invariant, which mitigates but does not remove this difference. Real gap processes, for example periodic sensor outages or interaction with labels, may differ. The natural datasets and PhysioNet 2012 only partly address this.
4. **Choice of γ.** γ was fixed at 1 on the development set; the confirmatory sensitivity analysis suggests γ≈0.5 is marginally better. We did not re-tune after seeing confirmatory results.
5. **Scope of the method.** The method is developed for MiniRocket's PPV pooling and univariate (or channel-wise multivariate) series. Observed-tap weighting was *not* applied to MultiRocket or Hydra, which were compared only after linear interpolation. Weighted versions of their pooling operators might gain similarly. Extending the approach to them and to genuinely irregular sampling times is left for future work.
6. **Implementation and energy.** Our numba implementation is slower than the optimised reference implementation of MiniRocket, so timing comparisons across implementations reflect engineering as well as method. Energy consumption was not measured; wall time on a fixed 4-core CPU serves as a proxy.
7. **Deep baselines.** Deep models other than GRU-D (e.g. BRITS, SAITS-based pipelines, Raindrop, mTAN) were not run. Nor was the end-to-end model of Yao et al. (2024): we did not use or verify a public implementation. Its reported results (MCAR only, a different dataset subset and protocol) are not comparable with ours, so we make no numerical comparison. On UCR, GRU-D was run only on a small, short-series subset because of CPU cost. No baseline was hyperparameter-tuned on our data; all used published defaults or common settings, as did MissRocket.


## 8 Conclusion

We asked how missing values should enter random-convolution time series classifiers and answered for MiniRocket, both analytically and in a pre-specified evaluation.

**The analysis.** Viewing the zero-sum MiniRocket response as a contrast of tap-group means yields a native estimator from observed taps. The same view explains why this estimator, although unbiased, loses to interpolation: its variance is higher. It also explains why interpolation fails inside long gaps, where it produces responses that do not depend on the signal.

**The method.** MissRocket keeps interpolated responses but weights their contribution to pooling by the fraction of observed taps. It adds no learned parameters, costs essentially nothing beyond MiniRocket and reduces to MiniRocket on complete data.

**The evidence.** Across 91 UCR datasets, MissRocket improved substantially on interpolation with MiniRocket when gaps were long or missingness depended on the values. It made no significant difference under scattered random gaps. It was much more robust when test data were more incomplete than training data, and on average it matched more expensive transforms.

**The limits.** The study also delineates the method's limits. kNN imputation was preferable for contiguous gaps in aligned datasets. Models that use the measurement pattern directly were clearly superior on sparse clinical records.

**Future work** includes:

- extending reliability-weighted pooling to MultiRocket's operators and to Hydra;
- selecting the gap filler per dataset;
- handling genuinely irregular time stamps.


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

Holm S (1979) A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics 6:65–70. https://www.jstor.org/stable/4615733

Horn M, Moor M, Bock C, Rieck B, Borgwardt K (2019) Set Functions for Time Series. arXiv:1909.12064. https://doi.org/10.48550/arXiv.1909.12064

Ismail Fawaz H, Forestier G, Weber J, Idoumghar L, Muller PA (2019) Deep learning for time series classification: a review. Data Mining and Knowledge Discovery 33:917–963. https://doi.org/10.1007/s10618-019-00619-1

Josse J, Chen JM, Prost N, Scornet E, Varoquaux G (2019) On the consistency of supervised learning with missing values. arXiv:1902.06931. https://doi.org/10.48550/arXiv.1902.06931

Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, Ye Q, Liu T-Y (2017) LightGBM: a highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30 (NIPS 2017). https://papers.nips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html

Kidger P, Morrill J, Foster J, Lyons T (2020) Neural Controlled Differential Equations for Irregular Time Series. arXiv:2005.08926. https://doi.org/10.48550/arXiv.2005.08926

Kim S, Kim H, Yun E, Lee H, Lee J, Lee J (2023) Probabilistic Imputation for Time-series Classification with Missing Data. arXiv:2308.06738. https://doi.org/10.48550/arXiv.2308.06738

Lam SK, Pitrou A, Seibert S (2015) Numba: a LLVM-based Python JIT compiler. In: Proceedings of the Second Workshop on the LLVM Compiler Infrastructure in HPC, pp 1–6. https://doi.org/10.1145/2833157.2833162

Le Morvan M, Josse J, Scornet E, Varoquaux G (2021) What's a good imputation to predict with missing values? arXiv:2106.00311. https://doi.org/10.48550/arXiv.2106.00311

Lipton ZC, Kale DC, Wetzel R (2016) Modeling Missing Data in Clinical Time Series with RNNs. arXiv:1606.04130. https://doi.org/10.48550/arXiv.1606.04130

Little R, Rubin D (2019) Statistical Analysis with Missing Data, Third Edition. Wiley. https://doi.org/10.1002/9781119482260

Liu G, Reda FA, Shih KJ, Wang TC, Tao A, Catanzaro B (2018) Image Inpainting for Irregular Holes Using Partial Convolutions. In: Computer Vision – ECCV 2018, pp 89–105. https://doi.org/10.1007/978-3-030-01252-6_6

Middlehurst M, Ismail-Fawaz A, Guillaume A et al (2024a) aeon: a Python toolkit for learning from time series. Journal of Machine Learning Research 25:1–10. https://jmlr.org/papers/v25/23-1444.html

Middlehurst M, Large J, Flynn M, Lines J, Bostrom A, Bagnall A (2021) HIVE-COTE 2.0: a new meta ensemble for time series classification. Machine Learning 110:3211–3243. https://doi.org/10.1007/s10994-021-06057-9

Middlehurst M, Schäfer P, Bagnall A (2024b) Bake off redux: a review and experimental evaluation of recent time series classification algorithms. Data Mining and Knowledge Discovery 38:1958–2031. https://doi.org/10.1007/s10618-024-01022-1

Mikalsen KØ, Bianchi FM, Soguero-Ruiz C, Jenssen R (2018) Time series cluster kernel for learning similarities between multivariate time series with missing data. Pattern Recognition 76:569–581. https://doi.org/10.1016/j.patcog.2017.11.030

Pedregosa F, Varoquaux G, Gramfort A et al (2011) Scikit-learn: machine learning in Python. Journal of Machine Learning Research 12:2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html

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


## Statements and Declarations

**Funding.** The authors declare that no funds, grants or other support were received during the preparation of this manuscript. [Authors: replace if applicable.]

**Competing interests.** The authors have no relevant financial or non-financial interests to disclose. [Authors: confirm.]

**Author contributions.** [To be completed by the authors on the separate title page and in the submission system, as required for double-anonymous review.]

**Data availability.** All data analysed in this study are publicly available:

- the UCR Time Series Classification Archive 2018 (Dau et al. 2019), obtained from timeseriesclassification.com;
- the PhysioNet/Computing in Cardiology Challenge 2012 data (Goldberger et al. 2000; Silva et al. 2012), available at https://physionet.org/content/challenge-2012/1.0.0/ under the Open Data Commons Attribution License v1.0.

The simulated missingness masks are fully determined by the published code and seeds. All raw per-run results (one row per dataset, condition, seed and method), the statistics files and the scripts that generate every table and figure are provided as Online Resources and in the code repository [link withheld for double-anonymous review].

**Code availability.** The complete source code, including the method, baselines, experiment scripts, statistical analysis, figure and table generation, and unit tests, is available in the code repository [link withheld for double-anonymous review]. It will be deposited in a public archive with a persistent identifier upon acceptance. `python run_all.py --mode full` reproduces all reported numbers.

**Ethics approval.** Not applicable. The study uses only public, de-identified benchmark data. The PhysioNet 2012 data were de-identified by the data providers and are distributed openly.

**Use of large language models.** The research workflow was carried out with the assistance of an AI agent (Anthropic Claude), as required to be documented by the journal's policy. Its use covered:

- literature and journal searching;
- code implementation;
- experiment orchestration;
- statistical analysis scripting;
- manuscript drafting.

All results reported in the manuscript are produced by the released code from the raw experimental outputs; no number was entered by hand. All references were verified against Crossref, arXiv, PubMed or the publishers' pages. The authors take full responsibility for the content. [Authors: adapt this statement to the actual division of work and to the journal's current policy text.]
