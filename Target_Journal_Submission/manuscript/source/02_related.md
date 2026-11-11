## 2 Related work

### 2.1 Random-convolution time series classification

ROCKET (Dempster et al. 2020) showed that thousands of random convolutional kernels, pooled by the proportion of positive values (PPV) and the maximum and followed by a linear classifier, rival far more expensive time series classifiers. MiniRocket (Dempster et al. 2021) replaced the random kernels by a small fixed set with weights in {−1, 2}, used PPV only, and became almost deterministic and up to two orders of magnitude faster. MultiRocket (Tan et al. 2022) added three pooling operators and a first-difference representation. Hydra (Dempster et al. 2023) turned the kernels into competing dictionary-like groups. QUANT (Dempster et al. 2024) showed that simple interval quantiles are similarly competitive. The bake-off of Middlehurst et al. (2024) confirmed that convolution-based methods offer the best accuracy-to-cost ratio among recent algorithms, with only heavy meta-ensembles such as HIVE-COTE 2 (Middlehurst et al. 2021) more accurate.

All of these methods assume complete, equal-length input. Benchmark practice follows suit: the standard UCR evaluation uses the 112 or 113 datasets without missing values or unequal lengths (Bagnall et al. 2017; Middlehurst et al. 2024), although the 2018 archive deliberately includes 15 incomplete or variable-length datasets (Dau et al. 2019). Where missing values must be handled, current studies zero-fill the series or pass NaNs through the transform to a learner that tolerates them. PYRREGULAR (Spinnato and Landi 2025) uses the latter approach, and in its benchmark of naturally irregular datasets MiniRocket nevertheless ranked first. To our knowledge, no previous work modifies the convolution response or the pooling of the ROCKET family to account for missingness.

### 2.2 Learning with missing values in time series

Deep missing-aware models encode the mask or time gaps inside a recurrent, attention or continuous-time architecture:
- GRU-D (Che et al. 2018), which decays inputs and hidden states toward empirical means;
- recurrent models with missingness indicators (Lipton et al. 2016);
- BRITS (Cao et al. 2018), with bidirectional recurrent imputation;
- multi-time attention networks (Shukla and Marlin 2021);
- set functions over observations (Horn et al. 2020);
- graph-guided networks for irregular multivariate series (Zhang et al. 2022);
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
