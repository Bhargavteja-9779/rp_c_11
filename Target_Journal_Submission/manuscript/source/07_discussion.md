## 7 Discussion

### 7.1 What the evidence supports

The experiments answer the motivating question in a nuanced but consistent way.

**First, native estimation from observed taps loses to interpolation.** The group-mean estimator is principled: it is exact on complete data, invariant to the level of the series, and unbiased under MCAR (Proposition 1). Yet it was significantly less accurate than MissRocket in every one of the nine confirmatory conditions, and in most conditions less accurate than plain interpolation as well. Proposition 2 explains why. Estimating a response from one or two taps per group inflates its variance up to fourfold. Interpolation, in contrast, exploits the smoothness of the signal to produce low-variance tap values whenever gaps are short. For random-convolution features, which are thresholded and pooled, variance appears to matter more than bias. We regard this negative result as useful: it rules out the most natural "missingness-aware" modification of the transform.

**Second, interpolation fails in a specific, identifiable way, and the failure can be repaired cheaply.** Inside a long gap, an interpolated window carries no information about the signal beyond the gap's two end points (Proposition 3); its response depends only on the slope between them. Weighting each response by the fraction of its taps that were observed removes these windows from the pooled statistics. Several results are consistent with this being the operative mechanism:

- the gain over unweighted interpolation is large under contiguous gaps and under value-dependent MNAR, where missing values cluster, and absent under scattered MCAR gaps;
- the gain grows with the missing rate under block and MNAR missingness, although dataset properties, gap length among them, explain little of the variation across datasets within a condition (Section 6.8);
- weighting also repairs LOCF filling, which produces fabricated *constant* segments;
- weighting does not improve kNN filling, which does not create such segments.

**Consistency with earlier benchmarks.** These findings are consistent with the observation that unadapted MiniRocket ranked first on naturally irregular datasets [@Spinnato2025]. MiniRocket with interpolation is a strong pipeline, and our natural-data results show it close to the best (Section 6.5). The gains from weighting concentrate where gaps are long.

**Third, robustness to train–test shift.** The robustness under train–test shift (Section 6.3) is, in our view, the most practically relevant result. A model trained on complete data and deployed on series with long gaps loses heavily with interpolation, and much less with observed-tap weighting. The industrial case study (Section 6.10) reproduces this on real vibration data, where the effect is far larger: interpolation turned outages into apparently healthy signals and caused missed faults, while MissRocket stayed close to its accuracy on complete data. When training data contained the same dropouts, by contrast, the choice of missing-value handling mattered little on CWRU.

### 7.2 What the evidence does not support

We do not claim that MissRocket is the best approach to classification with missing values in general.

- **Stronger transforms.** Pooled over all conditions, its advantage over MultiRocket and Hydra-MultiRocket is not statistically significant. Under 20% MCAR it is slightly worse than both.
- **kNN imputation.** Cross-series kNN imputation is more accurate on average under contiguous gaps, significantly so at 50%. In such settings the aligned training series contain more information about a missing segment than its two end points. The combination of kNN filling and weighting did not help (@tab:filler). The two approaches are complementary rather than nested, and choosing between them per dataset is an open question. In our ablation, selecting the configuration on the training set by leave-one-out did not improve accuracy.
- **Stronger transforms on matched data.** On CWRU, Hydra-MultiRocket was the most accurate method whenever training and test data had the same missingness. Its advantage disappeared, and it failed completely, once dropouts appeared only at test time.
- **The native estimator is not uniformly worse.** It lost to interpolation on UCR, but on the rough, broadband vibration signals of CWRU it slightly exceeded MissRocket when outages appeared only at test time. Which response estimator is preferable therefore depends on the smoothness of the signal (Proposition 2).
- **Boundary of applicability: sparse clinical records.** On PhysioNet 2012, both a deep missing-aware model (GRU-D) and gradient boosting with native missing-value handling were significantly better than every random-convolution method, MissRocket included. We regard this as a boundary of the method's applicability, not as noise. Shape-based kernels are poorly matched to very sparse, short, multivariate records in which the *presence* and *level* of measurements carry the signal. In these records, 80% of entries are missing and a "gap" is the normal state, not a sensor failure.

### 7.3 Deployment under sensor dropouts and decision rules

In condition monitoring and predictive maintenance, a classifier is usually trained on a curated archive of complete recordings and then run continuously on data from sensors that can drop out:

- a wireless node loses packets;
- an acquisition unit reconnects;
- an amplifier saturates.

Dropouts during operation therefore rarely match those in the training archive. Our results suggest that this mismatch, rather than the amount of missing data, is what makes missing-value handling critical. On CWRU, every method tolerated dropouts it had seen during training. Interpolation-based pipelines, however, lost most of their accuracy when long outages appeared only at test time, and their errors were mostly missed faults. For such deployments, a method whose features ignore fabricated windows is the safer default, even if a stronger transform is slightly more accurate on clean data. @tab:decision condenses the evidence into decision rules.

{#tab:decision} Decision rules for ROCKET-family classifiers on incomplete series, with the supporting evidence from this study. The rules summarise average behaviour on the data studied here; individual datasets can deviate

| Data situation | Recommended | Evidence | Caveat |
|:--------------------|:----------|:----------|:----------|
| Complete data | MiniRocket (fastest) or Hydra-MultiRocket (most accurate) | MissRocket reduces exactly to MiniRocket (Sect. 4.2); Hydra-MR best on complete CWRU (Sect. 6.10) | – |
| Scattered random loss of readings, also present in training data | MiniRocket + linear interpolation | No significant gain from weighting under MCAR (Sect. 6.1); on par on CWRU (Sect. 6.10) | Avoid zero or mean filling (Sect. 6.1) |
| Contiguous outages or value-dependent loss, also present in training data | MissRocket; or kNN imputation if training series are aligned and can be stored | Largest UCR gains under block and MNAR missingness (Sect. 6.1); kNN better on average for long gaps (Sect. 6.2) | On CWRU, where training data had the same outages, all methods were close and Hydra-MR was best (Sect. 6.10) |
| Trained on complete data, dropouts possible in operation (deployment shift) | MissRocket; the native estimator for rough, broadband signals | Robust under rate shift on UCR (Sect. 6.3) and under outage shift on CWRU, where interpolation-based pipelines failed (Sect. 6.10) | kNN imputation also degrades gracefully but needs the training set at prediction time |
| Tight memory or latency budget at the edge | MiniRocket-family transforms; avoid kNN imputation | Single-thread latency of a few ms per segment (Sect. 6.10) | Our MissRocket implementation is slower than aeon's MiniRocket (Sect. 6.6) |
| Sparse, irregular multivariate records with informative missingness (e.g. ICU) | GRU-D or gradient boosting with native missing-value handling | Both significantly better than all random-convolution methods on PhysioNet 2012 (Sect. 6.4) | Boundary of applicability of MissRocket |

Further practical notes:

- Zero and mean filling were the worst gap fillers in every UCR condition and should be avoided.
- With linear interpolation, observed-tap weighting (γ between 0.5 and 1) costs essentially nothing relative to the same implementation without weighting. Its mean accuracy on UCR was at most 0.7 pp below that of interpolation alone in any condition, although individual small datasets can lose more (Section 6.8).
- MissRocket processes each series independently and needs no training data at prediction time, unlike kNN imputation.

### 7.4 Limitations

1. **Seeds.** Infrastructure constraints (Section 5.5) limited the primary benchmark to one seed per dataset. Variability across seeds was assessed only on a 30-dataset subset (Section 6.9). The dataset, not the seed, is the unit of our statistical analysis, so additional seeds would mainly reduce within-dataset noise. That noise is substantial for datasets with very small test sets (Section 6.8).
2. **Dataset coverage.** The pre-specified compute rule excluded the {{N_EXCLUDED}} largest confirmatory datasets. The ablation, shift and sensitivity experiments use 30-dataset subsets, and the ablation uses a single missing rate.
3. **Simulated missingness.** Our mechanisms (MCAR, geometric blocks with a mean length of 10% of the series, logistic self-masking) are idealisations, and the gap length was not varied systematically. Within conditions, the realised gap length was only weakly associated with the gain (Section 6.8). No dataset in our benchmark has long *interior* gaps that arose naturally, so the long-gap results rest on simulation. The UCR series were z-normalised before values were removed, whereas in practice normalisation would use the observed values only. MissRocket's responses are offset-invariant, which mitigates but does not remove this difference. Real gap processes, for example periodic sensor outages or interaction with labels, may differ. The natural datasets and PhysioNet 2012 only partly address this.
4. **Choice of γ.** γ was fixed at 1 on the development set; the confirmatory sensitivity analysis suggests γ≈0.5 is marginally better. We did not re-tune after seeing confirmatory results.
5. **Scope of the method.** The method is developed for MiniRocket's PPV pooling and univariate (or channel-wise multivariate) series. Observed-tap weighting was *not* applied to MultiRocket or Hydra, which were compared only after linear interpolation. Weighted versions of their pooling operators might gain similarly. Extending the approach to them and to genuinely irregular sampling times is left for future work.
6. **Implementation and energy.** Our numba implementation is slower than the optimised reference implementation of MiniRocket, so timing comparisons across implementations reflect engineering as well as method. Energy consumption was not measured; wall time on a fixed 4-core CPU serves as a proxy.
7. **Industrial case study.** E9 uses one benchmark (CWRU) with simulated dropouts on real recordings, four load folds and, for most methods, one seed, so its results are descriptive. Not all CWRU records show clearly diagnosable fault signatures [@Smith2015]; the margins observed here may differ on other industrial data. Other machines, sensors, sampling rates and real dropout processes may behave differently, and GRU-D was not run on it. The edge-cost measurements used one thread of a server CPU as a proxy, not embedded hardware. E9 was added after external review (Section 5.5).
8. **Deep baselines.** Deep models other than GRU-D (e.g. BRITS, SAITS-based pipelines, Raindrop, mTAN) were not run. Nor was the end-to-end model of @Yao2024: we did not use or verify a public implementation. Its reported results (MCAR only, a different dataset subset and protocol) are not comparable with ours, so we make no numerical comparison. On UCR, GRU-D was run only on a small, short-series subset because of CPU cost. No baseline was hyperparameter-tuned on our data; all used published defaults or common settings, as did MissRocket.
