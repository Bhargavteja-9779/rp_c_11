# Review Round 2: Reviewer #2 (novelty, prior art, contribution differentiation)

**Focus:** Is the contribution genuinely new, or an obvious combination? Is the research gap real?

## Issues

| # | Severity | Issue | Required fix |
|---|---|---|---|
| 1 | **MAJOR** | *Masked pooling is standard.* Excluding padded or invalid positions from pooling is routine in sequence models (masked mean pooling over padding tokens), and partial convolutions renormalise by observed fractions. The paper must position observed-tap weighting relative to these ideas, or a reader will regard it as an obvious transfer. | Add a paragraph that (i) acknowledges masked pooling and renormalisation as the general idea, and (ii) states precisely what differs. Weights are *fractional window reliabilities* computed per dilation from the original mask, applied inside a *thresholded* (PPV) pooling of responses computed on *gap-filled* input. This keeps interpolation's low variance and suppresses only fabricated windows. In contrast, partial convolution modifies the response value, and masked pooling uses binary validity. Support the difference empirically: partial-convolution and binary support pooling (native estimator) are both worse. |
| 2 | MAJOR | *"Formal treatment" overclaims.* Propositions 1–4 are elementary algebra (the zero-sum identity; unbiasedness of a subset mean). Presenting them as a theoretical contribution invites "trivial" criticism. | Recast as "analysis" or "simple but consequential observations". Keep the propositions because they explain the experimental pattern, and say they are elementary. |
| 3 | MODERATE | *Novelty claims in Sect. 1 and 2.4.* "To our knowledge, no previous work modifies the convolution response or the pooling…": the search strategy should be documented. | Add a sentence on the search: terms, sources and date. Keep "to our knowledge". |
| 4 | MODERATE | *Relation to PYRREGULAR.* That benchmark found MiniRocket best on naturally irregular data *without* adaptation. A reader may conclude that adaptation is unnecessary. | Discuss explicitly: our natural-data results (Sect. 6.5) and theirs are consistent, because MiniRocket is strong; the gains of weighting concentrate where gaps are long. |
| 5 | MODERATE | *The strongest direct competitor is not run.* The end-to-end model of Yao et al. (2024) targets exactly UCR with MCAR and is not compared. | State in Limitations that no public implementation was used or verified, and that its reported setting (MCAR only, different protocol) is not comparable. Avoid any numerical comparison with its reported numbers. |
| 6 | MINOR | *The title does not name the main idea concisely.* | Keep the title. It accurately names the topic, the method and the evaluation; no change. |
| 7 | MINOR | *Contribution 4* lists findings, not contributions. | Acceptable for a journal article; rephrase as "Empirical evidence on…". |

## Is the research gap genuine?

Yes. A search on 2026-11-10/11 found:
- PYRREGULAR passes NaNs through sktime MiniRocket to LightGBM;
- POCKET zero-fills;
- Rhodes et al. (2025) change the imputer;
- Yao et al. (2024) is a deep model without ROCKET baselines.

No study found modifies the ROCKET-family transform or pooling for missingness, or evaluates such modifications across mechanisms. The gap is genuine but narrow, and the paper must not inflate it.

## Is the contribution incremental?

The *method* is a small modification. The paper's value rests on three things together:
- (a) a clear mechanism (fabricated windows) explaining *when* interpolation fails;
- (b) a cheap fix that addresses exactly that mechanism;
- (c) a large pre-specified evaluation that maps where it helps, where it does not, and where other approaches win.

The paper should make this framing explicit in the introduction and the discussion, rather than selling the method as a general solution. The current draft largely does this already.

---

## Author response and changes (Round 2)

| # | Action taken |
|---|---|
| 1 | Added Sect. 4.2 paragraph "Relation to masked pooling and partial convolution" with the precise distinction, and referenced the empirical evidence (partial-convolution variant and native support pooling worse; development log and Sect. 6.1). |
| 2 | Sect. 1 and contribution 1 now speak of an "analysis" with "elementary but consequential" propositions; Sect. 4.1 adds "These results are elementary". |
| 3 | Sect. 2.1 now documents the search (web and arXiv searches in November 2026, the search terms, and full reading of the closest works). |
| 4 | Sect. 7.1 discusses consistency with PYRREGULAR. |
| 5 | Limitation 7 states that Yao et al.'s model was not run and that its reported numbers are not comparable. |
| 7 | Contribution 4 rephrased. |
