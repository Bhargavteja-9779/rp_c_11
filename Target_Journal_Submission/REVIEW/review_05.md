# Review Round 5: Reviewer #5 (dataset validity, generalisation, domain shift, robustness, external validity, deployment)

**Stance:** try to invalidate the central claim, "observed-tap weighting helps when gaps are long or value-dependent and is safe otherwise".

## Attempts to invalidate, and outcomes

| # | Severity | Challenge | Assessment / action |
|---|---|---|---|
| 1 | **MAJOR** | *Mechanism shift.* All experiments use the same mechanism in training and test. In deployment the *type* of missingness can change, e.g. training data with sporadic dropouts and test data with long outages. Weighting might then hurt: the classifier is trained on features where weights are ≈ uniform and tested where many windows are zero-weighted. | **New experiment E4b (added in this round, post hoc and labelled as such):** MCAR→block and block→MCAR at 50% on the 30-dataset subset, comparing MissRocket, γ=0, MiniRocket+interp, kNN, native and LightGBM. Results are reported in Sect. 6.3 and Online Resource 1 (see the outcome below). |
| 2 | MAJOR | *Real long interior gaps are only simulated.* The natural datasets mostly have trailing (variable-length) gaps, and PhysioNet 2012 is negative. The central long-gap claim therefore rests on simulation. | Valid. Limitation 3 now states explicitly that no real dataset with long *interior* gaps was available in our benchmark. |
| 3 | MODERATE | *Normalisation order.* UCR series are z-normalised before values are deleted. In practice, normalisation would be computed on observed values only, which changes the level and scale of incomplete series. | Partly mitigated: MissRocket's responses are offset-invariant (zero-sum kernels), and the ridge head standardises features. Stated as a limitation; not tested. |
| 4 | MODERATE | *Dataset bias.* UCR datasets are mostly short, clean, univariate series with small training sets. | Acknowledged. The PhysioNet 2012 results show that conclusions do not transfer to sparse multivariate clinical records. |
| 5 | MINOR | *Deployment.* MissRocket processes each series independently and needs no training data at prediction time, unlike kNN imputation. Latency per series is comparable to MiniRocket. | Added a sentence to Sect. 7.3 (practical recommendations). |

## Outcome of E4b

The outcome is filled in after the run (see the table below, generated from `results/full/tables/table_mechanism_shift*.csv`).

---

## Author response

- 1: E4b was run. Results and interpretation are in Sect. 6.3 (paragraph "Mechanism shift"), including any adverse outcome.
- 2–3: Limitation 3 was extended (real interior gaps; normalisation order).
- 5: The deployment remark was added.
