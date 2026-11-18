## 8 Conclusion

We asked whether a fast random-convolution classifier can be made more reliable when sensor measurements are missing, without a learned imputation model and without increasing its computational complexity. We answered for MiniRocket, both analytically and in a pre-specified evaluation.

**The analysis.** Viewing the zero-sum MiniRocket response as a contrast of tap-group means yields a native estimator from observed taps. The same view explains why this estimator, although unbiased, loses to interpolation: its variance is higher. It also explains why interpolation fails inside long gaps, where it produces responses that do not depend on the signal.

**The method.** MissRocket keeps interpolated responses but weights their contribution to pooling by the fraction of observed taps. It adds no learned parameters and essentially no computation beyond MiniRocket's, and it reduces to MiniRocket on complete data.

**The evidence.** Across {{N_CONF}} UCR datasets, MissRocket improved substantially on interpolation with MiniRocket when gaps were long, and when missingness depended on the values at higher missing rates. It made no significant difference under scattered random gaps. It was much more robust when test data were more incomplete than training data, and on average it matched more expensive transforms. In a bearing-fault case study, it prevented the collapse of interpolation-based pipelines when sensor outages occurred only in operation, a collapse that took the form of missed faults.

**The limits.** The study also delineates the method's limits. kNN imputation was preferable for contiguous gaps in aligned datasets. When training data contained the same dropouts, stronger transforms such as Hydra-MultiRocket were more accurate on vibration data. Models that use the measurement pattern directly were clearly superior on sparse clinical records, which mark a boundary of the method's applicability.

**Future work** includes:

- extending reliability-weighted pooling to MultiRocket's operators and to Hydra;
- selecting the gap filler per dataset;
- handling genuinely irregular time stamps;
- validation on naturally occurring sensor dropouts and on embedded hardware.
