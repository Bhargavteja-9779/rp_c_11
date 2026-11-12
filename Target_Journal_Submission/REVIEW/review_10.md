# Review Round 10: Final adversarial review (independent; goal: find a reason to reject)

Conducted on the fully rebuilt manuscript after all experiments had completed (E1 seeds 0–2, E2–E7, E4b, scaling benchmark). It re-read the full assembled text and checked every quantitative statement against the generated tables.

## Search for a fatal flaw

| Candidate fatal flaw | Verdict |
|---|---|
| Data leakage inflating results | **Not found.** Leakage audit (review 3) re-confirmed: train-only fitting of imputers, biases, γ and penalties; independent masks; development/confirmatory separation. |
| Results not reproducible | **Not found.** 24 of 24 stored runs re-executed from scratch with exact equality (`tables/table_reproducibility_check.csv`). The unit tests pass. A fresh `run_all.py --mode quick` was executed (see final_audit.md). |
| Headline claim contradicted by own data | **Not found.** The pooled gain over MiniRocket+interpolation (+1.57 pp, p < 0.001) is significant. Every Holm-significant effect keeps its sign in all three seeds (machine-checked). |
| Undisclosed post-hoc method selection | **Not found.** All design iterations, including failures and the stale-code incident, are in the development log (Online Resource 1). The γ choice was frozen on development data; γ=0.5 being marginally better is disclosed. |
| Fabricated or unverifiable citations | **Not found.** All references verified (citation_audit.md). |

No fatal flaw was identified.

## Major weaknesses (all real; several fixed in this round)

1. **Incremental method.** The weighting is a small change. *Not fixable by revision; mitigated by framing.*
2. **Main long-gap evidence rests on simulated missingness.** *Disclosed (limitation 3).*
3. **Single-seed primary benchmark.** *Mitigated: three-seed subset analysis shows sign stability.*
4. **Protocol amendments forced by infrastructure.** *Disclosed in detail (Sect. 5.4).*
5. **Negative external validation (PhysioNet 2012).** *Reported prominently, including in the abstract.*
6. **kNN imputation dominates under contiguous gaps on average.** *Reported, including in the abstract.*
7. **Overclaims found in this round (FIXED):**
   - (a) "far less accurate than every ROCKET-family pipeline" was false at block 80% vs mean filling, and was restricted to interpolation/kNN pipelines;
   - (b) "beats them when missingness depends on the values" was restricted to MNAR 80%;
   - (c) "considerably more expensive transforms" became "five to six times more features and more memory";
   - (d) "at least as accurate on average" now states the non-significance;
   - (e) "MissRocket has the lowest peak memory" was withdrawn, because peak RSS includes library overhead;
   - (f) "all ROCKET-family methods perform similarly" on four natural datasets was false (DodgerLoopDay +3.3 pp) and was corrected;
   - (g) "clearly better" for every γ ∈ [0.25, 2] without a test became "higher mean accuracy";
   - (h) "carries no information about the signal" became "no information beyond the gap's end points";
   - (i) "results show this is the operative mechanism" became "consistent with";
   - (j) "kNN clearly better" became "more accurate on average, significantly at 50%";
   - (k) "never much worse than interpolation" became quantified (≤ 0.7 pp in mean; larger individual losses noted);
   - (l) "has the latency of MiniRocket" became "same asymptotic cost";
   - (m) untested causal explanations (block→MCAR gain; P12 failure; trailing-gap competitiveness) are now hedged as conjectures.
8. **Implementation slower than the reference.** *Disclosed; method cost separated from implementation cost by the controlled benchmark.*
9. **Baselines not tuned.** *Disclosed; applies equally to the proposed method.*
10. **No comparison with the closest deep competitor (Yao et al.).** *Disclosed; no public implementation used.*

## Moderate weaknesses

1. Long manuscript (34 pages, 11 tables, 7 figures in the main text).
2. The P12 single training run per method (bootstrap covers patient sampling only); disclosed.
3. E3/E4/E4b/E7 rest on 30 datasets; power is limited, and non-significance is declared inconclusive.
4. E4b was added post hoc; labelled as such.
5. The block-gap length is fixed at a 10% mean; disclosed.
6. Normalisation order (z-normalisation before removal); disclosed.
7. GRU-D on UCR is restricted to 17 small datasets; the interpretation is limited accordingly.
8. The error-analysis correlations are weak; reported as such after the pseudo-replication fix.
9. LightGBM uses different settings on P12 than on UCR; now stated.
10. Mask features are reported with a 1,000 budget that yields 924 features; corrected.
11. MultiRocket and Hydra were not given weighting; disclosed.
12. Channel-wise multivariate handling; disclosed.
13. Padding taps counted as observed; disclosed.
14. Bias sampling may include partially fabricated windows; noted in review 4.
15. Energy not measured; disclosed.
16. The quick-mode smoke-test slip on three confirmatory datasets; disclosed.
17. The stale-code development results (screening v1); retained but labelled STALE and not used.
18. Variable-length handling compared against resizing only (aeon has no native support); disclosed.

(Only 18 moderate issues are listed: no further genuine ones were found, and none was invented to reach a number.)

## Minor issues

- Caption numbering and order, list rendering and column-header wrapping: fixed in rounds 1, 7 and 10.
- Supplementary section numbering: fixed.

## Decision of this round

All scientifically defensible issues found have been fixed in text or code. The remaining weaknesses are disclosed limitations, not errors. **No re-run of experiments is required.**
