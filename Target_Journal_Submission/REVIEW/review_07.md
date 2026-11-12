# Review Round 7: Reviewer #7 (scientific writing, logic, unsupported claims, terminology, mathematics, figures/tables, references, guideline compliance)

## Unsupported or inaccurate statements (checked against primary sources)

| # | Severity | Statement in draft | Primary-source check | Fix |
|---|---|---|---|---|
| 1 | **MAJOR** | "MiniRocket … up to two orders of magnitude faster" (Sect. 2.1) | MiniRocket abstract (arXiv 2012.08791): "up to 75 times faster on larger datasets" | Corrected to "up to 75 times faster on larger datasets" |
| 2 | **MAJOR** | "The bake-off … confirmed that convolution-based methods offer the best accuracy-to-cost ratio … with only heavy meta-ensembles … more accurate" (Sect. 2.1); Intro: "reach accuracy close to the heaviest ensembles at a small fraction of their cost" | Bake-off redux abstract (arXiv 2304.13029): "two recently proposed algorithms, Hydra+MultiROCKET and HIVE-COTEv2, perform significantly better than other approaches" | Both sentences rewritten to state exactly this |
| 3 | MODERATE | "Yao et al. … compared only against deep models" | Full preprint text (pdftotext): "68 public univariate" UCR datasets; "comparisons with four state-of-the-art methods"; MCAR stated; the string "rocket" never occurs | Rephrased to the verifiable "their comparisons do not include ROCKET-family methods" |
| 4 | MODERATE | "Hydra … competing dictionary-like groups" | Title/abstract: competing convolutional kernels | Rephrased to describe the mechanism without the analogy |
| 5 | MODERATE | Intro: "twelve competitors" | E1 has 10 baselines + GRU-D = 11 | Corrected to "eleven" |
| 6 | MODERATE | Intro: "costs about the same as MiniRocket" | Our implementation is ~4× slower than aeon's MiniRocket (Table "efficiency") | "has the same asymptotic cost" |

## Mathematics (re-derived)

| Item | Check | Status |
|---|---|---|
| Eq. (2) from Eq. (1) | 2ΣP − ΣQ = 6(mean_P − mean_Q) since \|P\|=3, \|Q\|=6 | OK |
| Prop. 1(ii): zero-fill offset term | Δ = 2c·n_P − c·n_Q | OK |
| Partial-conv offset term | (2n_P − n_Q)c · 9/(n_P+n_Q) | OK |
| Prop. 2 | 36σ²(1/n_P+1/n_Q); complete 18σ²; worst case 72σ² ("fourfold") | OK |
| Prop. 3 | α cancels by the zero sum; C = βd(2Σ_P(j−4) − Σ_Q(j−4)) | OK |
| Prop. 4 | c=9 ⇒ w=1; γ=0 ⇒ w≡1 | OK |
| Notation | $\tilde C$ vs $\hat C$ used consistently (interpolated vs native) | OK |

## Structure and style

- The Results section is long (nine subsections). This is acceptable for a journal article; each subsection maps to one RQ or experiment.
- Bullet lists render correctly (verified in the PDF after the list-spacing fix).
- Terminology is consistent: "block" (contiguous gaps), "MCAR", "MNAR (self-masking)", "weighting", "γ".

## Figures and tables

- All figures are generated from result files at 300 dpi, with Springer-style "Fig. n" captions without end punctuation. Axis tick-label overlaps in the gap-length and sensitivity figures were fixed. Legend occlusion in the accuracy figure was fixed.
- Tables: captions above the tables; condition codes defined in the captions; the full per-condition statistics moved to Online Resource 1.

## Guideline compliance (JKSU-CIS / Springer, checked against the submission-guidelines page)

| Requirement | Status |
|---|---|
| Abstract 150–250 words | 198 words |
| 4–6 keywords | 6 |
| Decimal headings, ≤ 3 levels | Yes |
| Double-anonymous: no author-identifying information in the manuscript | Yes (repository link withheld); separate title page generated |
| Author–year citations, alphabetical reference list, DOIs as links | Yes (generated from verified metadata) |
| "Statements and Declarations" after References | Yes |
| Data availability statement | Yes |
| LLM use documented in Methods | Yes (Sect. 5.4 "Use of AI tools") |
| Figure captions "Fig. n" bold, no end punctuation | Yes |
| Supplementary files named "Online Resource" and cited | Yes (Online Resource 1, ESM_2.csv) |

All fixes were applied to the manuscript sources; the build was regenerated.
