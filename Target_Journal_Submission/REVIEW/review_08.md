# Review Round 8: Reviewer #8 (a competing researcher with a similar method; tries to show incrementality or unfairness)

## Arguments, and whether they hold

| # | Severity | Competitor's argument | Evidence / assessment | Action |
|---|---|---|---|---|
| 1 | MAJOR | **"The gain comes from interpolation, not from your weighting."** | Refuted. MissRocket vs its own γ=0 variant, same implementation, interpolation and seeds, differs only in the weights. On 91 datasets it gains +0.67/+2.98/+2.64 pp under block (20/50/80%) and +1.41/+2.90 pp under MNAR 50/80% (all Holm p ≤ 0.013) (Table 2). | None needed; stated in Sect. 6.2. |
| 2 | MAJOR | **"Block missingness with straight-line interpolation is constructed to favour you."** | Partly valid. The mechanisms were fixed before the confirmatory runs and geometric gaps are a standard dropout model, but the long-gap advantage is by construction where Prop. 3 applies. Counter-evidence: (i) weighting also helps LOCF filling, which produces constant rather than straight segments; (ii) gains under value-dependent MNAR, which is not designed for contiguity; (iii) gains under mechanism shift in *both* directions; (iv) natural variable-length data, where the advantage over interpolation is significant but not over resampling. | Discussion states that the long-gap evidence rests on simulation (limitation 3). |
| 3 | MAJOR | **"A fair comparison would give MultiRocket/Hydra the same weighting."** | Valid scope limitation. Weighting was designed for PPV; MultiRocket's other operators (MPV, MIPV, LSPV) need separate treatment. Our claim is restricted to "MissRocket matches them on average", not "beats them". | Limitation 5 states this explicitly (done in round 1). |
| 4 | MODERATE | **"kNN imputation already solves long gaps; your niche is small."** | Partly valid: kNN wins under block at 20–50% (significant at 50%). But kNN loses heavily under MCAR/MNAR (up to 8.4 pp), needs the training set at prediction time, and weighting does not combine with it. The niches are complementary. | Stated in Sect. 6.1, 7.2, 7.3. |
| 5 | MODERATE | **"For variable-length data, use native unequal-length support, not padding."** | Checked: aeon 1.6's MiniRocket reports `capability:unequal_length = False`. The library's documented options are padding, truncation or resizing. We compared against resizing ("resampling") and padding plus interpolation. | Footnote-level clarification added to the caption of Table (natural). |
| 6 | MODERATE | **"γ was tuned."** | γ=1 was fixed on 10 development datasets. The confirmatory sensitivity shows γ=0.5 marginally better; we do not switch to it. | Reported transparently (Sect. 6.7). |
| 7 | MINOR | **"Your 'native estimator' is a straw man."** | It is the most natural principled alternative (unbiased, offset-invariant). It is included as a negative result with an explanation, not as a straw-man baseline, and we did not tune it differently from MissRocket. | None. |
| 8 | MINOR | **"Equivalence to MiniRocket on complete data is trivial."** | Agreed. It is stated as a sanity property, not as a contribution. | None. |

## Verdict of this round

The incrementality criticism is partly fair: the method is a small modification. The work's value lies in the mechanism, the cheap fix and the extensive evidence, including evidence *against* the method's generality. That framing is already used in the paper. No claim needs to be withdrawn. One clarification was added (arg. 5).
