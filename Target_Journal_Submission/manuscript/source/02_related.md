## 2 Related work

### 2.1 Random-convolution time series classification

ROCKET [@Dempster2020] showed that thousands of random convolutional kernels, pooled by the proportion of positive values (PPV) and the maximum and followed by a linear classifier, rival far more expensive time series classifiers. MiniRocket [@Dempster2021] replaced the random kernels by a small fixed set with weights in {−1, 2}, used PPV only, and became almost deterministic and up to 75 times faster on larger datasets. MultiRocket [@Tan2022] added three pooling operators and a first-difference representation. Hydra [@Dempster2023] organises random kernels into competing groups and counts which kernel in each group matches best. QUANT [@Dempster2024] showed that simple interval quantiles are similarly competitive. The bake-off of @Middlehurst2024 found Hydra combined with MultiRocket, together with the meta-ensemble HIVE-COTE 2 [@Middlehurst2021], to be significantly more accurate than all other approaches.

All of these methods assume complete, equal-length input. Benchmark practice follows suit: the standard UCR evaluation uses the 112 or 113 datasets without missing values or unequal lengths [@Bagnall2017; @Middlehurst2024], although the 2018 archive deliberately includes 15 incomplete or variable-length datasets [@Dau2019]. Where missing values must be handled, current studies zero-fill the series or pass NaNs through the transform to a learner that tolerates them. PYRREGULAR [@Spinnato2025] uses the latter approach, and in its benchmark of naturally irregular datasets MiniRocket nevertheless ranked first. To our knowledge, no previous work modifies the convolution response or the pooling of the ROCKET family to account for missingness; missing-aware classifiers in general are, of course, well established (Section 2.2). This conclusion rests on web and arXiv searches carried out in November 2026, combining ROCKET, MiniRocket, MultiRocket, Hydra and QUANT with missing values, NaN, masks, masked or partial convolution, imputation and irregular series, and on reading the closest works in full.

### 2.2 Learning with missing values in time series

Deep learning for complete series is reviewed by @IsmailFawaz2019. Deep missing-aware models encode the mask or time gaps inside a recurrent, attention or continuous-time architecture:

- GRU-D [@Che2018], which decays inputs and hidden states toward empirical means;
- recurrent models with missingness indicators [@Lipton2016];
- BRITS [@Cao2018], with bidirectional recurrent imputation;
- multi-time attention networks [@Shukla2021];
- set functions over observations [@Horn2020];
- graph-guided networks for irregular multivariate series [@Zhang2022];
- neural controlled differential equations [@Kidger2020].

Other approaches impute first and then classify, using statistical, kernel-based or learned imputers. Examples include the time series cluster kernel [@Mikalsen2018] and the self-attention imputer SAITS [@Du2023]. @Kim2023 instead train a probabilistic imputer jointly with the classifier. Closest to our setting, @Yao2024 trained a GRU imputer jointly with a multi-scale convolutional classifier on 68 UCR datasets with simulated MCAR missingness; their comparisons do not include ROCKET-family methods. @Rhodes2025 proposed label-guided imputation using forest-based proximities, including proximities derived from ROCKET, and evaluated it on 85 UCR datasets under MCAR, MAR and MNAR with downstream random-forest and k-NN classifiers. Their method changes the imputer, not the transform.

### 2.3 Theory and practice of missing-value handling

For supervised prediction, @Josse2019 and @LeMorvan2021 showed that impute-then-predict can be Bayes-consistent for almost any imputation, provided the learner is flexible enough. Adding missingness indicators helps when missingness is informative [@Lipton2016; @VanNess2023]. Large benchmarks on health data found that native handling of missing values in tree ensembles, which goes back to approaches such as missing-incorporated-in-attributes [@Twala2008], and indicator features often match or beat sophisticated imputation [@PerezLebel2022].

These results assume flexible learners. ROCKET-family classifiers are instead *fixed* random-feature maps followed by a linear model, so how missingness enters the feature map matters directly. In image inpainting, partial convolutions renormalise each response by the fraction of observed inputs [@Liu2018]. Section 4.1 shows that this renormalisation breaks the zero-sum structure of MiniRocket kernels.

**Positioning of the proposed weighting.** Down-weighting or excluding unobserved inputs is an old idea, and we do not claim it as new. The method is related to three established techniques:

- *Missing indicators* [@Lipton2016; @VanNess2023] add the mask as extra features and leave the value features unchanged; in our ablation the analogous mask-pattern features did not help (Section 6.2).
- *Masked (weighted) pooling* averages only over valid positions. MissRocket is a soft version of it, applied to the PPV operator, with weights given by the observed fraction of each kernel window rather than by a binary validity flag.
- *Partial convolution* [@Liu2018] renormalises the response itself, which for zero-sum kernels injects the level of the series into the response through the missingness pattern (Section 4.1). MissRocket leaves the response unchanged and acts only on its weight in pooling (Section 4.2 details the differences).

What we contribute is therefore not the principle but its analysis and its placement in the ROCKET family:

- the tap-group-mean decomposition, which shows *why* the natural native estimator is unbiased but too noisy (Propositions 1–2) and *where* interpolation fails (Proposition 3);
- the choice of acting on the pooling weights rather than on the response, which keeps MiniRocket exact on complete data and keeps its asymptotic cost;
- a pre-specified evaluation against imputation, native estimation, indicator features, stronger transforms and missing-aware models.

### 2.4 Gap addressed by this study

The literature therefore lacks:

- (i) a principled treatment of missingness inside random-convolution transforms;
- (ii) evidence on how imputation, native estimation, reliability weighting and indicator features compare for these classifiers across missingness mechanisms (MCAR, long gaps, value-dependent MNAR) and rates;
- (iii) an assessment of robustness to train–test missingness shift and on naturally incomplete data.

This study addresses all three under a pre-specified protocol with a separate development set.
