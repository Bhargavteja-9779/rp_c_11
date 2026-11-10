# Research Pipeline Progress Log

Auto-resume instructions: read this file and `git log`, then continue from the first unchecked item.
Package root: `Target_Journal_Submission/`. Code: `Target_Journal_Submission/code/`.

## Status
- [x] Phase 0: target journal selected. JKSU-CIS (Springer Nature); measured median received→accepted 66 d; JIF 6.4.
- [~] Phases 1–5: topic = missing values in random-convolution time-series classification (ROCKET family).
- [~] Phases 6–10: core transform (numba), missingness simulator, imputers, runner, tests (17 passing).
- [ ] Phases 11–20: confirmatory experiments
- [ ] Phases 21–42: manuscript, reviews, DOCX, package

## Protocol decisions (pre-registered before confirmatory runs)
- UCR 2018: 113 complete datasets. A development set of 10 is used for design decisions: the 5 pilot datasets
  (ArrowHead, GunPoint, ECG200, Wafer, ShapesAll) plus 5 drawn at random with seed 2026 (CinCECGTorso, MoteStrain,
  MixedShapesSmallTrain, DistalPhalanxOutlineAgeGroup, MiddlePhalanxOutlineAgeGroup).
  The remaining 103 are confirmatory. The 15 natural-missing/variable-length datasets are used for external validation.
- Fixed UCR train/test splits. Missingness is simulated independently for train and test with deterministic, hashed seeds.

## Negative / iteration log (Phase 19)
1. Pilot (dev): the unbiased group-mean masked estimator ("MaskRocket") is much WORSE than linear interpolation +
   MiniRocket on ArrowHead under MCAR (0.697 vs 0.857 at 30%). Hypothesis: high variance and loss of temporal smoothness.
2. Confidence-weighted pooling on interpolated input ("WRocket", weight = (observed taps/9)^gamma) is also worse than
   plain interpolation, and monotonically worse as gamma increases (dev, first 6 settings).
3. The LightGBM baseline was initially degenerate on small training sets (min_child_samples=20 gave majority-class
   predictions). Fixed (min_child_samples=5) before any confirmatory run; dev rows rerun.
