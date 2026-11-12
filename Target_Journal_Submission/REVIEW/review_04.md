# Review Round 4: Reviewer #4 (ML methodology, architecture, training protocol, implementation correctness; code inspected)

**Code inspected:**
- `src/models/maskrocket.py`: `_taps`, `_responses`, `_fit_biases`, `_transform`;
- `src/models/missrocket.py`: `_transform_hist`, `MissRocket`, `MissRocketMV`;
- `src/models/methods.py`, `src/models/grud.py`, `src/preprocessing/imputation.py`, `src/training/runner.py`;
- `experiments/*.py`, `scripts/analyze.py`, `scripts/error_analysis.py`;
- the unit tests (18 passing).

## Code ↔ manuscript consistency

| Manuscript statement | Code | Status |
|---|---|---|
| Kernels, dilations, padding alternation and bias quantiles follow MiniRocket | `_fit_dilations`, `_quantiles`, `p1 = (p0 + k) % 2` in `_transform*` | Consistent. Accuracy reproduces aeon's reference on complete data (pilot). |
| Out-of-bounds taps under zero padding count as observed zeros | `_taps`: `idx<0 or idx>=L → V=0, O=1` | Consistent |
| Eq. (5): PPV weighted by $(c/9)^\gamma$ | `_transform_hist`: per-count histograms × `wtab` | Consistent. Test: γ=1 histogram features equal direct weighted features (max diff 3.6e-7). |
| Biases from positions with c(t) ≥ 1 of a random training series | `_fit_biases(..., _wtab([1.0])[0])`: S>0 iff c≥1 | Consistent |
| Ridge head with α ∈ {10⁻³,…,10³} and LOO selection | `RidgeClassifierCV(alphas=np.logspace(-3,3,10))` | Consistent |
| γ=0 ⇒ MiniRocket on the interpolated series | weight table of ones | Consistent (Prop. 4; unit test) |
| Native estimator = group-mean responses + support pooling, no mask features | `MaskRocket-noC` | Consistent |
| "Missingness-pattern features: 1,000 features" | `MaskRocket(num_features=1000)` → 84×11 = **924** | **Inconsistent → fixed** in the text ("budget of 1,000; 924 after rounding") |
| GRU-D: 64 units, Adam 1e-3, batch 64, ≤60 epochs, stratified 20% validation | `run_grud` defaults; **patience 8** not stated | **Fixed** (patience stated) |
| Linear interpolation; edge handling not stated | `impute_linear`: nearest observed value at the edges | **Fixed** (stated in Sect. 4.2) |
| LightGBM settings (300 trees, …) | UCR as stated; **P12 uses 500 trees, lr 0.03, min_child_samples 20** | **Inconsistent → fixed** (P12 settings added to Sect. 5.3) |
| P12 per-channel budget 252 + 84 mask features | `e5_p12.py`, `MissRocketMV` | Consistent |
| Timing includes gap filling | `_rocket_pipeline`, `run_missrocket` time spans | Consistent |

## Methodological concerns

| # | Severity | Issue | Response |
|---|---|---|---|
| 1 | MODERATE | *Zero padding counts as observed.* Edge windows of a series with missing ends receive high weight from artificial padding zeros. | This is inherited from MiniRocket's design so as to keep exact equivalence on complete data (Prop. 4). It is now stated in Sect. 4.2. A variant treating padding as unobserved is a possible refinement, not evaluated. |
| 2 | MODERATE | *Bias sampling from interpolated series.* Biases are quantiles of responses that may themselves include fabricated windows (c ≥ 1 but small). | Correct observation. Biases are drawn from windows with at least one observed tap. Weighting the quantiles was not explored. Noted as future work; no change to the results. |
| 3 | MINOR | *Determinism.* Multithreaded reductions (fastmath pooling, BLAS) can change the last bits of features. | Stated in the README (Determinism); unit tests bound the differences (≤1e-6). |
| 4 | MINOR | *Multivariate handling* is channel-wise with independent biases, which ignores cross-channel kernels (unlike MiniRocket's multivariate variant). | Stated in Sect. 4.3. Fair across methods, because all ROCKET-family methods on P12 are channel-wise. |

No implementation error affecting the reported results was found in this round. The inconsistencies above were documentation errors; all are corrected in the manuscript.
