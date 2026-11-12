## 7 Discussion

### 7.1 What the evidence supports

The experiments answer the motivating question in a nuanced but consistent way.

**First, native estimation from observed taps loses to interpolation.** The group-mean estimator is principled: it is exact on complete data, invariant to the level of the series, and unbiased under MCAR (Proposition 1). Yet it was significantly less accurate than MissRocket in every one of the nine confirmatory conditions, and in most conditions less accurate than plain interpolation as well. Proposition 2 explains why. Estimating a response from one or two taps per group inflates its variance up to fourfold. Interpolation, in contrast, exploits the smoothness of the signal to produce low-variance tap values whenever gaps are short. For random-convolution features, which are thresholded and pooled, variance appears to matter more than bias. We regard this negative result as useful: it rules out the most natural "missingness-aware" modification of the transform.

**Second, interpolation fails in a specific, identifiable way, and the failure can be repaired cheaply.** Inside a long gap, an interpolated window carries no information about the signal (Proposition 3); its response depends only on the slope between the gap's two end points. Weighting each response by the fraction of its taps that were observed removes these windows from the pooled statistics. Several results show that this is the operative mechanism:
- the gain over unweighted interpolation is large under contiguous gaps and under value-dependent MNAR, where missing values cluster, and absent under scattered MCAR gaps;
- the gain grows with the realised mean gap length;
- weighting also repairs LOCF filling, which produces fabricated *constant* segments;
- weighting does not improve kNN filling, which does not create such segments.

**Third, robustness to train–test shift.** The robustness under train–test shift (Section 6.3) is, in our view, the most practically relevant result. A model trained on complete data and deployed on series with long gaps loses heavily with interpolation, and much less with observed-tap weighting.

### 7.2 What the evidence does not support

We do not claim that MissRocket is the best approach to classification with missing values in general.
- **Stronger transforms.** Pooled over all conditions, its advantage over MultiRocket and Hydra-MultiRocket is not statistically significant. Under 20% MCAR it is slightly worse than both.
- **kNN imputation.** Cross-series kNN imputation is clearly better under contiguous gaps. In such settings the aligned training series contain more information about a missing segment than its two end points. The combination of kNN filling and weighting did not help (@tab:filler). The two approaches are complementary rather than nested, and choosing between them per dataset is an open question. Training-set selection by leave-one-out was not reliable in our ablation.
- **Sparse clinical records.** On PhysioNet 2012, both a deep missing-aware model (GRU-D) and gradient boosting with native missing-value handling were significantly better than every random-convolution method, MissRocket included. Shape-based kernels are poorly matched to very sparse, short, multivariate records in which the *presence* and *level* of measurements carry the signal.

### 7.3 Practical recommendations

Our evidence supports the following guidance for practitioners using ROCKET-family classifiers on incomplete series:
- Avoid zero and mean filling; they were the worst gap fillers in every condition.
- Use linear interpolation together with observed-tap weighting (γ between 0.5 and 1). This costs essentially nothing over MiniRocket and is never much worse than interpolation alone. It helps substantially when gaps are long, when missingness depends on the values, or when test data may be more incomplete than training data.
- If gaps are long and the training series are well aligned, try kNN imputation.
- For sparse multivariate clinical records, prefer models that use the measurement pattern directly.

### 7.4 Limitations

1. **Seeds.** Infrastructure constraints (Section 5.4) limited the primary benchmark to one seed per dataset. Variability across seeds was assessed only on a 30-dataset subset (Section 6.9). The dataset, not the seed, is the unit of our statistical analysis, so additional seeds would mainly reduce within-dataset noise. That noise is substantial for datasets with very small test sets (Section 6.8).
2. **Dataset coverage.** The pre-registered compute rule excluded the {{N_EXCLUDED}} largest confirmatory datasets. The ablation and shift experiments use a 30-dataset subset at a single rate.
3. **Simulated missingness.** Our mechanisms (MCAR, geometric blocks, logistic self-masking) are idealisations. Real gap processes, for example periodic sensor outages or interaction with labels, may differ. The natural datasets and PhysioNet 2012 only partly address this.
4. **Choice of γ.** γ was fixed at 1 on the development set; the confirmatory sensitivity analysis suggests γ≈0.5 is marginally better. We did not re-tune after seeing confirmatory results.
5. **Scope of the method.** The method is developed for MiniRocket's PPV pooling and univariate (or channel-wise multivariate) series. Extending it to MultiRocket's additional pooling operators, to Hydra's competing kernels and to genuinely irregular sampling times is left for future work.
6. **Implementation.** Our numba implementation is slower than the optimised reference implementation of MiniRocket. Timing comparisons across implementations therefore reflect engineering as well as method.
7. **Deep baselines.** Deep models other than GRU-D (e.g. BRITS, SAITS-based pipelines, Raindrop, mTAN) and the end-to-end model of @Yao2024 were not run. On UCR, GRU-D was run only on a small, short-series subset because of CPU cost.
