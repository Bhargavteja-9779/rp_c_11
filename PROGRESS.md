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
4. Dev screening, 8 datasets × 6 settings: dilation-aware hybrid "GapRocket" is worse than interpolation (0.760 vs 0.789 on the
   first 5 datasets). Hypothesis H-gap rejected.
5. Dev: feature fusion (interpolated ‖ group-mean) gives no gain over a feature-matched 20k control (23 W / 22 L). Rejected.
6. Dev finding: regime dependence. Observed-tap-weighted pooling (gamma=1) beats interpolation under block missingness
   (+1.6/+2.4 pts at 30/60%) but loses under MCAR (−1.8/−3.7 pts). This motivates the FINAL METHOD, MissRocket:
   interpolation + observed-tap-weighted PPV with gamma∈{0,.5,1,2} × mask-features∈{off,on} selected on TRAIN by the
   ridge LOO (GCV) score. gamma=0 is exactly interpolation+MiniRocket. Next step: dev screening of MissRocket,
   then freeze the protocol.
7. INTEGRITY ISSUE FOUND AND FIXED. The dev rows for WRocket-noC (and possibly other variants) generated 2026-11-10 22:03–22:14
   do not match the current code. The current code gives identical features for WRocket-noC and MissRocket-g1 (max
   diff 3.6e-7), yet the stored accuracies differ systematically (e.g. ArrowHead MCAR +0.09). Cause: rows produced by
   different intermediate code versions during optimisation, possibly worsened by numba's cache not tracking
   cross-file njit changes. Remedy: (a) all experiment entry points clear numba caches before running; (b) the full dev
   screening is redone under one frozen code version in results/dev/dev_screening_v2.csv. Earlier dev conclusions
   (items 1–6) are provisional until then. The old file is retained as results/dev/dev_viability_STALE.csv.
8. Dev screening v2 (frozen code, 8 dev datasets × 48 settings): fixed gamma=1 weighting is best (mean acc 0.8213, rank 4.39)
   vs interpolation + MiniRocket (0.8108 own / 0.8093 aeon); LOO selection 0.8187; native estimators 0.75–0.79.
   DECISION: primary method = MissRocket with gamma=1, no mask (selection, other gammas, mask and gap filler become ablations).
9. PROTOCOL SLIP (disclosed): the first quick-mode pipeline check ran on 3 CONFIRMATORY datasets (Coffee,
   ItalyPowerDemand, SyntheticControl). Results there showed kNN imputation as a strong baseline. Quick mode now uses
   dev datasets only. kNN gap filling had not been screened, so it is screened ON THE DEV SET ONLY
   (results/dev/dev_screening_v2.csv) before freezing.
10. Dev kNN screening: kNN filling helps under block 60% but hurts under MCAR 60%; weighting adds nothing on kNN fills.
    Overall linear + gamma=1 is still best (0.8213 vs 0.8136/0.8143). Primary method unchanged; kNN variants added to E3.
11. PROTOCOL FROZEN at the commit titled "PROTOCOL FREEZE". Confirmatory runs (E1–E7) start after it with this code and config.

## Confirmatory runs (started 2026-11-11 03:17 UTC)
- E1 runs in the background: `cd Target_Journal_Submission/code && nohup python3 run_all.py --mode full --only E1 > logs/full_E1.log 2>&1 &`
- `scripts/chain_full.sh` waits for E1, then runs `run_all.py --mode full`, which covers E3, E5a, E5b, E4, E7, E2, the analysis,
  the method figures and the E8 error analysis.
- Estimated time: E1 ≈ 14 h; the rest ≈ 10 h.
- **If the container restarted**, background jobs are gone. Restart with:
  `cd Target_Journal_Submission/code && nohup python3 run_all.py --mode full > logs/full_all.log 2>&1 &`
  All experiments are resumable and skip finished rows.
- Check progress with: `tail -1 logs/full_E1.log logs/full_all.log; wc -l results/full/*/raw_results.csv`
- After the runs: build the manuscript (manuscript/source/*.md with {{placeholders}} filled from results/full/statistics),
  then 10 review rounds, DOCX/PDF, cover letter, final package.
