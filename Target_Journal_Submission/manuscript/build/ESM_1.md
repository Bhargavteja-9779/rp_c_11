*Online Resource 1 — Missing values in random-convolution time series classification: observed-tap weighting for MiniRocket and a pre-specified evaluation. Journal of King Saud University – Computer and Information Sciences. [Author names and affiliations withheld for double-anonymous review]*


## S1 Development log (design iterations, negative results, protocol issues)

Verbatim from the project's version-controlled progress log. Items refer to the development datasets unless stated otherwise.

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


## S2 Dataset lists


**Eligible confirmatory datasets (91):** ACSF1, Adiac, BME, Beef, BeetleFly, BirdChicken, CBF, Car, Chinatown, ChlorineConcentration, Coffee, Computers, CricketX, CricketY, CricketZ, DiatomSizeReduction, DistalPhalanxOutlineCorrect, DistalPhalanxTW, ECG5000, ECGFiveDays, EOGHorizontalSignal, EOGVerticalSignal, Earthquakes, EthanolLevel, FaceAll, FaceFour, FacesUCR, FiftyWords, Fish, FreezerRegularTrain, FreezerSmallTrain, Fungi, GunPointAgeSpan, GunPointMaleVersusFemale, GunPointOldVersusYoung, Ham, Haptics, Herring, HouseTwenty, InlineSkate, InsectEPGRegularTrain, InsectEPGSmallTrain, InsectWingbeatSound, ItalyPowerDemand, LargeKitchenAppliances, Lightning2, Lightning7, Meat, MedicalImages, MiddlePhalanxOutlineCorrect, MiddlePhalanxTW, OSULeaf, OliveOil, PhalangesOutlinesCorrect, PigAirwayPressure, PigArtPressure, PigCVP, Plane, PowerCons, ProximalPhalanxOutlineAgeGroup, ProximalPhalanxOutlineCorrect, ProximalPhalanxTW, RefrigerationDevices, Rock, ScreenType, SemgHandGenderCh2, SemgHandMovementCh2, SemgHandSubjectCh2, ShapeletSim, SmallKitchenAppliances, SmoothSubspace, SonyAIBORobotSurface1, SonyAIBORobotSurface2, Strawberry, SwedishLeaf, Symbols, SyntheticControl, ToeSegmentation1, ToeSegmentation2, Trace, TwoLeadECG, TwoPatterns, UMD, UWaveGestureLibraryX, UWaveGestureLibraryY, UWaveGestureLibraryZ, Wine, WordSynonyms, Worms, WormsTwoClass, Yoga

**Confirmatory datasets excluded by the pre-specified compute rule (12):** Crop, ElectricDevices, FordA, FordB, HandOutlines, Mallat, MixedShapesRegularTrain, NonInvasiveFetalECGThorax1, NonInvasiveFetalECGThorax2, Phoneme, StarLightCurves, UWaveGestureLibraryAll

**Development datasets (10):** ArrowHead, CinCECGTorso, DistalPhalanxOutlineAgeGroup, ECG200, GunPoint, MiddlePhalanxOutlineAgeGroup, MixedShapesSmallTrain, MoteStrain, ShapesAll, Wafer

**Natural (incomplete / variable-length) datasets (15):** AllGestureWiimoteX, AllGestureWiimoteY, AllGestureWiimoteZ, DodgerLoopDay, DodgerLoopGame, DodgerLoopWeekend, GestureMidAirD1, GestureMidAirD2, GestureMidAirD3, GesturePebbleZ1, GesturePebbleZ2, MelbournePedestrian, PLAID, PickupGestureWiimoteZ, ShakeGestureWiimoteZ

**30-dataset subset (seeds 1–2, E3, E4; random draw, seed 11):** BME, CBF, ChlorineConcentration, Computers, DistalPhalanxOutlineCorrect, EOGHorizontalSignal, EOGVerticalSignal, Earthquakes, Fish, FreezerRegularTrain, FreezerSmallTrain, Haptics, HouseTwenty, InlineSkate, Meat, MiddlePhalanxOutlineCorrect, MiddlePhalanxTW, OSULeaf, OliveOil, PigCVP, PowerCons, ProximalPhalanxTW, ShapeletSim, SonyAIBORobotSurface2, Strawberry, Symbols, ToeSegmentation2, UWaveGestureLibraryX, UWaveGestureLibraryY, UWaveGestureLibraryZ

## S3 Full per-condition statistics (E1, seed 0, accuracy)

Δ = MissRocket − baseline (accuracy, proportion). CI: percentile bootstrap over datasets (10,000 resamples). p_holm: Holm correction within condition over ten baselines.

| mechanism | rate | baseline | n_datasets | mean_diff | median_diff | ci95_low | ci95_high | wins | ties | losses | rank_biserial | p_value | p_holm |
|:--------------------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| block | 0.2000 | MiniRocket + linear interp. | 91 | 0.0108 | 0.0058 | 0.0045 | 0.0174 | 55 | 12 | 24 | 0.4418 | <0.001 | 0.002 |
| block | 0.2000 | MiniRocket + zero fill | 91 | 0.0446 | 0.0349 | 0.0328 | 0.0573 | 70 | 10 | 11 | 0.8519 | <0.001 | <0.001 |
| block | 0.2000 | MiniRocket + mean fill | 91 | 0.0479 | 0.0344 | 0.0342 | 0.0623 | 75 | 3 | 13 | 0.8016 | <0.001 | <0.001 |
| block | 0.2000 | MiniRocket + LOCF | 91 | 0.0250 | 0.0193 | 0.0155 | 0.0352 | 65 | 7 | 19 | 0.6230 | <0.001 | <0.001 |
| block | 0.2000 | MiniRocket + kNN impute | 91 | -0.0182 | 0.0000 | -0.0340 | -0.0042 | 38 | 9 | 44 | -0.1931 | 0.159 | 0.219 |
| block | 0.2000 | MultiRocket + linear interp. | 91 | -0.0012 | -0.0040 | -0.0108 | 0.0092 | 33 | 8 | 50 | -0.1931 | 0.109 | 0.219 |
| block | 0.2000 | Hydra-MultiRocket + linear interp. | 91 | -0.0029 | -0.0040 | -0.0120 | 0.0071 | 31 | 10 | 50 | -0.2352 | 0.055 | 0.164 |
| block | 0.2000 | Native masked MiniRocket (group-mean) | 91 | 0.0413 | 0.0271 | 0.0282 | 0.0557 | 68 | 6 | 17 | 0.7237 | <0.001 | <0.001 |
| block | 0.2000 | LightGBM (native NaN) | 91 | 0.1253 | 0.1000 | 0.0895 | 0.1644 | 71 | 3 | 17 | 0.7572 | <0.001 | <0.001 |
| block | 0.2000 | 1-NN ED + linear interp. | 91 | 0.1760 | 0.1409 | 0.1455 | 0.2095 | 85 | 2 | 4 | 0.9610 | <0.001 | <0.001 |
| block | 0.5000 | MiniRocket + linear interp. | 91 | 0.0394 | 0.0256 | 0.0285 | 0.0516 | 79 | 5 | 7 | 0.8327 | <0.001 | <0.001 |
| block | 0.5000 | MiniRocket + zero fill | 91 | 0.0635 | 0.0597 | 0.0475 | 0.0797 | 75 | 4 | 12 | 0.8103 | <0.001 | <0.001 |
| block | 0.5000 | MiniRocket + mean fill | 91 | 0.0860 | 0.0872 | 0.0700 | 0.1023 | 79 | 2 | 10 | 0.8946 | <0.001 | <0.001 |
| block | 0.5000 | MiniRocket + LOCF | 91 | 0.0590 | 0.0467 | 0.0453 | 0.0733 | 73 | 5 | 13 | 0.8375 | <0.001 | <0.001 |
| block | 0.5000 | MiniRocket + kNN impute | 91 | -0.0302 | -0.0051 | -0.0535 | -0.0098 | 40 | 3 | 48 | -0.2587 | 0.040 | 0.040 |
| block | 0.5000 | MultiRocket + linear interp. | 91 | 0.0240 | 0.0133 | 0.0109 | 0.0393 | 57 | 7 | 27 | 0.4683 | <0.001 | <0.001 |
| block | 0.5000 | Hydra-MultiRocket + linear interp. | 91 | 0.0174 | 0.0095 | 0.0047 | 0.0320 | 53 | 3 | 35 | 0.3210 | 0.009 | 0.019 |
| block | 0.5000 | Native masked MiniRocket (group-mean) | 91 | 0.0488 | 0.0390 | 0.0343 | 0.0644 | 68 | 3 | 20 | 0.6992 | <0.001 | <0.001 |
| block | 0.5000 | LightGBM (native NaN) | 91 | 0.0989 | 0.0782 | 0.0649 | 0.1349 | 64 | 3 | 24 | 0.6685 | <0.001 | <0.001 |
| block | 0.5000 | 1-NN ED + linear interp. | 91 | 0.1689 | 0.1415 | 0.1372 | 0.2032 | 78 | 6 | 7 | 0.9343 | <0.001 | <0.001 |
| block | 0.8000 | MiniRocket + linear interp. | 91 | 0.0446 | 0.0267 | 0.0309 | 0.0595 | 69 | 4 | 18 | 0.7450 | <0.001 | <0.001 |
| block | 0.8000 | MiniRocket + zero fill | 91 | 0.0557 | 0.0408 | 0.0394 | 0.0732 | 72 | 3 | 16 | 0.7186 | <0.001 | <0.001 |
| block | 0.8000 | MiniRocket + mean fill | 91 | 0.0845 | 0.0607 | 0.0659 | 0.1040 | 73 | 3 | 15 | 0.8938 | <0.001 | <0.001 |
| block | 0.8000 | MiniRocket + LOCF | 91 | 0.0621 | 0.0439 | 0.0464 | 0.0797 | 74 | 3 | 14 | 0.8631 | <0.001 | <0.001 |
| block | 0.8000 | MiniRocket + kNN impute | 91 | -0.0052 | 0.0009 | -0.0282 | 0.0169 | 46 | 4 | 41 | -0.0057 | 0.997 | 0.997 |
| block | 0.8000 | MultiRocket + linear interp. | 91 | 0.0281 | 0.0159 | 0.0148 | 0.0428 | 60 | 5 | 26 | 0.5164 | <0.001 | <0.001 |
| block | 0.8000 | Hydra-MultiRocket + linear interp. | 91 | 0.0279 | 0.0115 | 0.0141 | 0.0426 | 62 | 4 | 25 | 0.4984 | <0.001 | <0.001 |
| block | 0.8000 | Native masked MiniRocket (group-mean) | 91 | 0.0353 | 0.0237 | 0.0212 | 0.0502 | 65 | 7 | 19 | 0.5807 | <0.001 | <0.001 |
| block | 0.8000 | LightGBM (native NaN) | 91 | 0.0602 | 0.0502 | 0.0364 | 0.0856 | 64 | 1 | 26 | 0.5560 | <0.001 | <0.001 |
| block | 0.8000 | 1-NN ED + linear interp. | 91 | 0.1315 | 0.1000 | 0.1078 | 0.1564 | 81 | 5 | 5 | 0.9733 | <0.001 | <0.001 |
| mcar | 0.2000 | MiniRocket + linear interp. | 91 | -0.0036 | 0.0000 | -0.0096 | 0.0010 | 27 | 28 | 36 | -0.1195 | 0.328 | 0.328 |
| mcar | 0.2000 | MiniRocket + zero fill | 91 | 0.0768 | 0.0483 | 0.0578 | 0.0984 | 80 | 4 | 7 | 0.9342 | <0.001 | <0.001 |
| mcar | 0.2000 | MiniRocket + mean fill | 91 | 0.0771 | 0.0462 | 0.0579 | 0.1002 | 81 | 5 | 5 | 0.9652 | <0.001 | <0.001 |
| mcar | 0.2000 | MiniRocket + LOCF | 91 | 0.0080 | 0.0018 | 0.0030 | 0.0139 | 46 | 20 | 25 | 0.4077 | 0.004 | 0.012 |
| mcar | 0.2000 | MiniRocket + kNN impute | 91 | 0.0146 | 0.0095 | 0.0011 | 0.0305 | 59 | 8 | 24 | 0.4521 | <0.001 | 0.001 |
| mcar | 0.2000 | MultiRocket + linear interp. | 91 | -0.0024 | -0.0020 | -0.0099 | 0.0067 | 24 | 17 | 50 | -0.3654 | 0.004 | 0.012 |
| mcar | 0.2000 | Hydra-MultiRocket + linear interp. | 91 | -0.0042 | -0.0054 | -0.0105 | 0.0030 | 26 | 13 | 52 | -0.3749 | 0.003 | 0.012 |
| mcar | 0.2000 | Native masked MiniRocket (group-mean) | 91 | 0.0391 | 0.0200 | 0.0259 | 0.0548 | 71 | 8 | 12 | 0.7926 | <0.001 | <0.001 |
| mcar | 0.2000 | LightGBM (native NaN) | 91 | 0.1677 | 0.1312 | 0.1295 | 0.2095 | 76 | 5 | 10 | 0.9070 | <0.001 | <0.001 |
| mcar | 0.2000 | 1-NN ED + linear interp. | 91 | 0.1676 | 0.1366 | 0.1372 | 0.2013 | 83 | 4 | 4 | 0.9911 | <0.001 | <0.001 |
| mcar | 0.5000 | MiniRocket + linear interp. | 91 | -0.0058 | 0.0000 | -0.0135 | 0.0002 | 35 | 11 | 45 | -0.1272 | 0.301 | 0.330 |
| mcar | 0.5000 | MiniRocket + zero fill | 91 | 0.1261 | 0.0867 | 0.0980 | 0.1557 | 79 | 4 | 8 | 0.9289 | <0.001 | <0.001 |
| mcar | 0.5000 | MiniRocket + mean fill | 91 | 0.1329 | 0.1018 | 0.1056 | 0.1621 | 81 | 5 | 5 | 0.9527 | <0.001 | <0.001 |
| mcar | 0.5000 | MiniRocket + LOCF | 91 | 0.0182 | 0.0110 | 0.0089 | 0.0294 | 61 | 10 | 20 | 0.6158 | <0.001 | <0.001 |
| mcar | 0.5000 | MiniRocket + kNN impute | 91 | 0.0454 | 0.0336 | 0.0211 | 0.0709 | 64 | 5 | 22 | 0.6212 | <0.001 | <0.001 |
| mcar | 0.5000 | MultiRocket + linear interp. | 91 | -0.0033 | -0.0017 | -0.0124 | 0.0068 | 32 | 12 | 47 | -0.1915 | 0.120 | 0.330 |
| mcar | 0.5000 | Hydra-MultiRocket + linear interp. | 91 | -0.0061 | 0.0000 | -0.0141 | 0.0020 | 33 | 14 | 44 | -0.2174 | 0.110 | 0.330 |
| mcar | 0.5000 | Native masked MiniRocket (group-mean) | 91 | 0.0852 | 0.0538 | 0.0637 | 0.1078 | 80 | 2 | 9 | 0.8931 | <0.001 | <0.001 |
| mcar | 0.5000 | LightGBM (native NaN) | 91 | 0.2106 | 0.1875 | 0.1695 | 0.2534 | 78 | 1 | 12 | 0.9121 | <0.001 | <0.001 |
| mcar | 0.5000 | 1-NN ED + linear interp. | 91 | 0.1650 | 0.1370 | 0.1350 | 0.1981 | 84 | 2 | 5 | 0.9655 | <0.001 | <0.001 |
| mcar | 0.8000 | MiniRocket + linear interp. | 91 | 0.0031 | 0.0000 | -0.0030 | 0.0093 | 42 | 9 | 40 | 0.1693 | 0.240 | 0.257 |
| mcar | 0.8000 | MiniRocket + zero fill | 91 | 0.1628 | 0.1461 | 0.1333 | 0.1940 | 83 | 2 | 6 | 0.9396 | <0.001 | <0.001 |
| mcar | 0.8000 | MiniRocket + mean fill | 91 | 0.1812 | 0.1562 | 0.1515 | 0.2112 | 83 | 4 | 4 | 0.9833 | <0.001 | <0.001 |
| mcar | 0.8000 | MiniRocket + LOCF | 91 | 0.0435 | 0.0295 | 0.0319 | 0.0559 | 71 | 4 | 16 | 0.7855 | <0.001 | <0.001 |
| mcar | 0.8000 | MiniRocket + kNN impute | 91 | 0.0836 | 0.0673 | 0.0517 | 0.1166 | 66 | 5 | 20 | 0.6509 | <0.001 | <0.001 |
| mcar | 0.8000 | MultiRocket + linear interp. | 91 | 0.0060 | 0.0028 | -0.0026 | 0.0145 | 48 | 5 | 38 | 0.1919 | 0.129 | 0.257 |
| mcar | 0.8000 | Hydra-MultiRocket + linear interp. | 91 | 0.0076 | 0.0023 | -0.0006 | 0.0160 | 48 | 8 | 35 | 0.2361 | 0.067 | 0.200 |
| mcar | 0.8000 | Native masked MiniRocket (group-mean) | 91 | 0.1183 | 0.0883 | 0.0937 | 0.1444 | 81 | 1 | 9 | 0.9272 | <0.001 | <0.001 |
| mcar | 0.8000 | LightGBM (native NaN) | 91 | 0.2439 | 0.2195 | 0.2002 | 0.2885 | 77 | 1 | 13 | 0.9179 | <0.001 | <0.001 |
| mcar | 0.8000 | 1-NN ED + linear interp. | 91 | 0.1521 | 0.1396 | 0.1252 | 0.1819 | 83 | 2 | 6 | 0.9628 | <0.001 | <0.001 |
| mnar | 0.2000 | MiniRocket + linear interp. | 91 | 0.0042 | 0.0000 | -0.0015 | 0.0114 | 37 | 21 | 33 | 0.0853 | 0.557 | 0.557 |
| mnar | 0.2000 | MiniRocket + zero fill | 91 | 0.0510 | 0.0376 | 0.0377 | 0.0655 | 71 | 8 | 12 | 0.8531 | <0.001 | <0.001 |
| mnar | 0.2000 | MiniRocket + mean fill | 91 | 0.0588 | 0.0420 | 0.0446 | 0.0740 | 74 | 10 | 7 | 0.9157 | <0.001 | <0.001 |
| mnar | 0.2000 | MiniRocket + LOCF | 91 | 0.0105 | 0.0052 | 0.0035 | 0.0183 | 53 | 15 | 23 | 0.4405 | <0.001 | 0.002 |
| mnar | 0.2000 | MiniRocket + kNN impute | 91 | 0.0145 | 0.0107 | 0.0037 | 0.0244 | 57 | 13 | 21 | 0.5427 | <0.001 | <0.001 |
| mnar | 0.2000 | MultiRocket + linear interp. | 91 | 0.0039 | 0.0000 | -0.0052 | 0.0152 | 34 | 13 | 44 | -0.1470 | 0.248 | 0.497 |
| mnar | 0.2000 | Hydra-MultiRocket + linear interp. | 91 | 0.0020 | 0.0000 | -0.0062 | 0.0119 | 32 | 14 | 45 | -0.1948 | 0.129 | 0.387 |
| mnar | 0.2000 | Native masked MiniRocket (group-mean) | 91 | 0.0310 | 0.0222 | 0.0206 | 0.0423 | 70 | 6 | 15 | 0.7335 | <0.001 | <0.001 |
| mnar | 0.2000 | LightGBM (native NaN) | 91 | 0.1525 | 0.1089 | 0.1155 | 0.1933 | 78 | 2 | 11 | 0.8851 | <0.001 | <0.001 |
| mnar | 0.2000 | 1-NN ED + linear interp. | 91 | 0.1721 | 0.1467 | 0.1423 | 0.2056 | 86 | 2 | 3 | 0.9925 | <0.001 | <0.001 |
| mnar | 0.5000 | MiniRocket + linear interp. | 91 | 0.0156 | 0.0039 | 0.0067 | 0.0268 | 53 | 13 | 25 | 0.4297 | <0.001 | 0.002 |
| mnar | 0.5000 | MiniRocket + zero fill | 91 | 0.0755 | 0.0559 | 0.0569 | 0.0957 | 74 | 2 | 15 | 0.8377 | <0.001 | <0.001 |
| mnar | 0.5000 | MiniRocket + mean fill | 91 | 0.0915 | 0.0583 | 0.0701 | 0.1145 | 76 | 3 | 12 | 0.8807 | <0.001 | <0.001 |
| mnar | 0.5000 | MiniRocket + LOCF | 91 | 0.0276 | 0.0198 | 0.0172 | 0.0389 | 66 | 3 | 22 | 0.6231 | <0.001 | <0.001 |
| mnar | 0.5000 | MiniRocket + kNN impute | 91 | 0.0430 | 0.0382 | 0.0242 | 0.0625 | 63 | 6 | 22 | 0.5858 | <0.001 | <0.001 |
| mnar | 0.5000 | MultiRocket + linear interp. | 91 | 0.0104 | -0.0032 | -0.0013 | 0.0244 | 38 | 6 | 47 | 0.0164 | 0.991 | 1.000 |
| mnar | 0.5000 | Hydra-MultiRocket + linear interp. | 91 | 0.0080 | 0.0000 | -0.0022 | 0.0202 | 38 | 9 | 44 | -0.0053 | 0.887 | 1.000 |
| mnar | 0.5000 | Native masked MiniRocket (group-mean) | 91 | 0.0361 | 0.0278 | 0.0234 | 0.0491 | 69 | 2 | 20 | 0.6230 | <0.001 | <0.001 |
| mnar | 0.5000 | LightGBM (native NaN) | 91 | 0.1544 | 0.1299 | 0.1182 | 0.1945 | 69 | 4 | 18 | 0.8548 | <0.001 | <0.001 |
| mnar | 0.5000 | 1-NN ED + linear interp. | 91 | 0.1840 | 0.1439 | 0.1541 | 0.2172 | 87 | 2 | 2 | 0.9895 | <0.001 | <0.001 |
| mnar | 0.8000 | MiniRocket + linear interp. | 91 | 0.0331 | 0.0260 | 0.0221 | 0.0451 | 70 | 4 | 17 | 0.6669 | <0.001 | <0.001 |
| mnar | 0.8000 | MiniRocket + zero fill | 91 | 0.0651 | 0.0439 | 0.0459 | 0.0851 | 69 | 3 | 19 | 0.7051 | <0.001 | <0.001 |
| mnar | 0.8000 | MiniRocket + mean fill | 91 | 0.0877 | 0.0795 | 0.0689 | 0.1078 | 77 | 2 | 12 | 0.8944 | <0.001 | <0.001 |
| mnar | 0.8000 | MiniRocket + LOCF | 91 | 0.0554 | 0.0407 | 0.0408 | 0.0700 | 70 | 4 | 17 | 0.7589 | <0.001 | <0.001 |
| mnar | 0.8000 | MiniRocket + kNN impute | 91 | 0.0656 | 0.0487 | 0.0391 | 0.0939 | 61 | 4 | 26 | 0.5745 | <0.001 | <0.001 |
| mnar | 0.8000 | MultiRocket + linear interp. | 91 | 0.0195 | 0.0052 | 0.0045 | 0.0360 | 51 | 8 | 32 | 0.3018 | 0.017 | 0.017 |
| mnar | 0.8000 | Hydra-MultiRocket + linear interp. | 91 | 0.0231 | 0.0116 | 0.0092 | 0.0383 | 53 | 7 | 31 | 0.3697 | 0.004 | 0.007 |
| mnar | 0.8000 | Native masked MiniRocket (group-mean) | 91 | 0.0333 | 0.0231 | 0.0185 | 0.0481 | 61 | 5 | 25 | 0.5595 | <0.001 | <0.001 |
| mnar | 0.8000 | LightGBM (native NaN) | 91 | 0.1473 | 0.1275 | 0.1140 | 0.1833 | 73 | 1 | 17 | 0.8711 | <0.001 | <0.001 |
| mnar | 0.8000 | 1-NN ED + linear interp. | 91 | 0.1669 | 0.1547 | 0.1392 | 0.1964 | 83 | 2 | 6 | 0.9705 | <0.001 | <0.001 |


## S4 Secondary metrics (E1, seed 0): mean balanced accuracy and macro-F1


| mechanism | rate | method | mean_accuracy | std_accuracy | mean_balanced_accuracy | mean_macro_f1 |
|:--------------------|----------:|----------:|----------:|----------:|----------:|----------:|
| block | 0.2000 | MissRocket (proposed) | 0.7913 | 0.1599 | 0.7675 | 0.7641 |
| block | 0.2000 | MiniRocket + linear interp. | 0.7806 | 0.1636 | 0.7576 | 0.7531 |
| block | 0.2000 | MiniRocket + zero fill | 0.7467 | 0.1745 | 0.7218 | 0.7166 |
| block | 0.2000 | MiniRocket + mean fill | 0.7435 | 0.1741 | 0.7183 | 0.7138 |
| block | 0.2000 | MiniRocket + LOCF | 0.7664 | 0.1699 | 0.7417 | 0.7366 |
| block | 0.2000 | MiniRocket + kNN impute | 0.8095 | 0.1544 | 0.7870 | 0.7841 |
| block | 0.2000 | MultiRocket + linear interp. | 0.7925 | 0.1584 | 0.7691 | 0.7655 |
| block | 0.2000 | Hydra-MultiRocket + linear interp. | 0.7942 | 0.1568 | 0.7714 | 0.7683 |
| block | 0.2000 | Native masked MiniRocket (group-mean) | 0.7501 | 0.1735 | 0.7242 | 0.7192 |
| block | 0.2000 | LightGBM (native NaN) | 0.6660 | 0.2143 | 0.6404 | 0.6341 |
| block | 0.2000 | 1-NN ED + linear interp. | 0.6154 | 0.2047 | 0.5976 | 0.5863 |
| block | 0.2000 | w/o weighting (γ=0) | 0.7847 | 0.1613 | 0.7612 | 0.7568 |
| block | 0.5000 | MissRocket (proposed) | 0.6914 | 0.1889 | 0.6642 | 0.6579 |
| block | 0.5000 | MiniRocket + linear interp. | 0.6520 | 0.1931 | 0.6231 | 0.6159 |
| block | 0.5000 | MiniRocket + zero fill | 0.6279 | 0.1832 | 0.5972 | 0.5912 |
| block | 0.5000 | MiniRocket + mean fill | 0.6054 | 0.1923 | 0.5755 | 0.5674 |
| block | 0.5000 | MiniRocket + LOCF | 0.6324 | 0.1910 | 0.6029 | 0.5946 |
| block | 0.5000 | MiniRocket + kNN impute | 0.7216 | 0.1795 | 0.6965 | 0.6908 |
| block | 0.5000 | MultiRocket + linear interp. | 0.6674 | 0.1936 | 0.6384 | 0.6333 |
| block | 0.5000 | Hydra-MultiRocket + linear interp. | 0.6741 | 0.1936 | 0.6448 | 0.6402 |
| block | 0.5000 | Native masked MiniRocket (group-mean) | 0.6426 | 0.1865 | 0.6126 | 0.6058 |
| block | 0.5000 | LightGBM (native NaN) | 0.5926 | 0.2147 | 0.5615 | 0.5529 |
| block | 0.5000 | 1-NN ED + linear interp. | 0.5225 | 0.2105 | 0.5028 | 0.4932 |
| block | 0.5000 | w/o weighting (γ=0) | 0.6617 | 0.1924 | 0.6326 | 0.6255 |
| block | 0.8000 | MissRocket (proposed) | 0.5606 | 0.1965 | 0.5298 | 0.5201 |
| block | 0.8000 | MiniRocket + linear interp. | 0.5160 | 0.2065 | 0.4873 | 0.4780 |
| block | 0.8000 | MiniRocket + zero fill | 0.5049 | 0.2024 | 0.4751 | 0.4679 |
| block | 0.8000 | MiniRocket + mean fill | 0.4761 | 0.2042 | 0.4459 | 0.4358 |
| block | 0.8000 | MiniRocket + LOCF | 0.4985 | 0.2113 | 0.4667 | 0.4574 |
| block | 0.8000 | MiniRocket + kNN impute | 0.5658 | 0.2084 | 0.5372 | 0.5278 |
| block | 0.8000 | MultiRocket + linear interp. | 0.5325 | 0.2061 | 0.5063 | 0.4981 |
| block | 0.8000 | Hydra-MultiRocket + linear interp. | 0.5328 | 0.2050 | 0.5065 | 0.4980 |
| block | 0.8000 | Native masked MiniRocket (group-mean) | 0.5253 | 0.1924 | 0.4945 | 0.4866 |
| block | 0.8000 | LightGBM (native NaN) | 0.5004 | 0.2126 | 0.4709 | 0.4588 |
| block | 0.8000 | 1-NN ED + linear interp. | 0.4291 | 0.2134 | 0.4108 | 0.4013 |
| block | 0.8000 | w/o weighting (γ=0) | 0.5342 | 0.2003 | 0.5055 | 0.4961 |
| mcar | 0.2000 | MissRocket (proposed) | 0.8495 | 0.1448 | 0.8279 | 0.8259 |
| mcar | 0.2000 | MiniRocket + linear interp. | 0.8531 | 0.1431 | 0.8317 | 0.8296 |
| mcar | 0.2000 | MiniRocket + zero fill | 0.7728 | 0.1736 | 0.7465 | 0.7417 |
| mcar | 0.2000 | MiniRocket + mean fill | 0.7724 | 0.1766 | 0.7447 | 0.7402 |
| mcar | 0.2000 | MiniRocket + LOCF | 0.8415 | 0.1465 | 0.8205 | 0.8184 |
| mcar | 0.2000 | MiniRocket + kNN impute | 0.8350 | 0.1525 | 0.8151 | 0.8118 |
| mcar | 0.2000 | MultiRocket + linear interp. | 0.8520 | 0.1413 | 0.8312 | 0.8288 |
| mcar | 0.2000 | Hydra-MultiRocket + linear interp. | 0.8537 | 0.1396 | 0.8331 | 0.8312 |
| mcar | 0.2000 | Native masked MiniRocket (group-mean) | 0.8104 | 0.1590 | 0.7858 | 0.7815 |
| mcar | 0.2000 | LightGBM (native NaN) | 0.6818 | 0.2115 | 0.6533 | 0.6460 |
| mcar | 0.2000 | 1-NN ED + linear interp. | 0.6820 | 0.2053 | 0.6652 | 0.6582 |
| mcar | 0.2000 | w/o weighting (γ=0) | 0.8533 | 0.1435 | 0.8321 | 0.8301 |
| mcar | 0.5000 | MissRocket (proposed) | 0.8237 | 0.1516 | 0.8011 | 0.7979 |
| mcar | 0.5000 | MiniRocket + linear interp. | 0.8296 | 0.1478 | 0.8065 | 0.8034 |
| mcar | 0.5000 | MiniRocket + zero fill | 0.6977 | 0.1807 | 0.6687 | 0.6605 |
| mcar | 0.5000 | MiniRocket + mean fill | 0.6908 | 0.1801 | 0.6600 | 0.6514 |
| mcar | 0.5000 | MiniRocket + LOCF | 0.8056 | 0.1588 | 0.7820 | 0.7782 |
| mcar | 0.5000 | MiniRocket + kNN impute | 0.7783 | 0.1639 | 0.7551 | 0.7493 |
| mcar | 0.5000 | MultiRocket + linear interp. | 0.8270 | 0.1493 | 0.8047 | 0.8020 |
| mcar | 0.5000 | Hydra-MultiRocket + linear interp. | 0.8298 | 0.1472 | 0.8078 | 0.8052 |
| mcar | 0.5000 | Native masked MiniRocket (group-mean) | 0.7386 | 0.1688 | 0.7109 | 0.7029 |
| mcar | 0.5000 | LightGBM (native NaN) | 0.6131 | 0.2031 | 0.5787 | 0.5673 |
| mcar | 0.5000 | 1-NN ED + linear interp. | 0.6587 | 0.2055 | 0.6406 | 0.6309 |
| mcar | 0.5000 | w/o weighting (γ=0) | 0.8305 | 0.1457 | 0.8077 | 0.8049 |
| mcar | 0.8000 | MissRocket (proposed) | 0.7445 | 0.1600 | 0.7206 | 0.7150 |
| mcar | 0.8000 | MiniRocket + linear interp. | 0.7414 | 0.1658 | 0.7160 | 0.7105 |
| mcar | 0.8000 | MiniRocket + zero fill | 0.5817 | 0.1842 | 0.5513 | 0.5425 |
| mcar | 0.8000 | MiniRocket + mean fill | 0.5633 | 0.1872 | 0.5325 | 0.5224 |
| mcar | 0.8000 | MiniRocket + LOCF | 0.7010 | 0.1744 | 0.6731 | 0.6661 |
| mcar | 0.8000 | MiniRocket + kNN impute | 0.6609 | 0.1838 | 0.6304 | 0.6199 |
| mcar | 0.8000 | MultiRocket + linear interp. | 0.7385 | 0.1694 | 0.7153 | 0.7093 |
| mcar | 0.8000 | Hydra-MultiRocket + linear interp. | 0.7369 | 0.1675 | 0.7137 | 0.7082 |
| mcar | 0.8000 | Native masked MiniRocket (group-mean) | 0.6262 | 0.1827 | 0.5952 | 0.5852 |
| mcar | 0.8000 | LightGBM (native NaN) | 0.5006 | 0.1992 | 0.4638 | 0.4498 |
| mcar | 0.8000 | 1-NN ED + linear interp. | 0.5924 | 0.1986 | 0.5711 | 0.5625 |
| mcar | 0.8000 | w/o weighting (γ=0) | 0.7434 | 0.1627 | 0.7185 | 0.7139 |
| mnar | 0.2000 | MissRocket (proposed) | 0.8338 | 0.1471 | 0.8134 | 0.8109 |
| mnar | 0.2000 | MiniRocket + linear interp. | 0.8296 | 0.1512 | 0.8073 | 0.8051 |
| mnar | 0.2000 | MiniRocket + zero fill | 0.7829 | 0.1634 | 0.7583 | 0.7542 |
| mnar | 0.2000 | MiniRocket + mean fill | 0.7750 | 0.1665 | 0.7501 | 0.7453 |
| mnar | 0.2000 | MiniRocket + LOCF | 0.8233 | 0.1521 | 0.8001 | 0.7976 |
| mnar | 0.2000 | MiniRocket + kNN impute | 0.8193 | 0.1505 | 0.7972 | 0.7942 |
| mnar | 0.2000 | MultiRocket + linear interp. | 0.8299 | 0.1521 | 0.8090 | 0.8068 |
| mnar | 0.2000 | Hydra-MultiRocket + linear interp. | 0.8318 | 0.1500 | 0.8112 | 0.8091 |
| mnar | 0.2000 | Native masked MiniRocket (group-mean) | 0.8029 | 0.1557 | 0.7775 | 0.7740 |
| mnar | 0.2000 | LightGBM (native NaN) | 0.6813 | 0.2127 | 0.6535 | 0.6461 |
| mnar | 0.2000 | 1-NN ED + linear interp. | 0.6617 | 0.2044 | 0.6445 | 0.6365 |
| mnar | 0.2000 | w/o weighting (γ=0) | 0.8301 | 0.1500 | 0.8073 | 0.8048 |
| mnar | 0.5000 | MissRocket (proposed) | 0.7904 | 0.1574 | 0.7660 | 0.7613 |
| mnar | 0.5000 | MiniRocket + linear interp. | 0.7748 | 0.1690 | 0.7500 | 0.7444 |
| mnar | 0.5000 | MiniRocket + zero fill | 0.7149 | 0.1760 | 0.6895 | 0.6825 |
| mnar | 0.5000 | MiniRocket + mean fill | 0.6989 | 0.1711 | 0.6709 | 0.6632 |
| mnar | 0.5000 | MiniRocket + LOCF | 0.7627 | 0.1677 | 0.7369 | 0.7314 |
| mnar | 0.5000 | MiniRocket + kNN impute | 0.7473 | 0.1651 | 0.7236 | 0.7182 |
| mnar | 0.5000 | MultiRocket + linear interp. | 0.7800 | 0.1682 | 0.7563 | 0.7520 |
| mnar | 0.5000 | Hydra-MultiRocket + linear interp. | 0.7823 | 0.1644 | 0.7582 | 0.7538 |
| mnar | 0.5000 | Native masked MiniRocket (group-mean) | 0.7542 | 0.1589 | 0.7280 | 0.7211 |
| mnar | 0.5000 | LightGBM (native NaN) | 0.6359 | 0.2072 | 0.6054 | 0.5963 |
| mnar | 0.5000 | 1-NN ED + linear interp. | 0.6063 | 0.1959 | 0.5856 | 0.5764 |
| mnar | 0.5000 | w/o weighting (γ=0) | 0.7762 | 0.1681 | 0.7519 | 0.7468 |
| mnar | 0.8000 | MissRocket (proposed) | 0.6982 | 0.1620 | 0.6720 | 0.6627 |
| mnar | 0.8000 | MiniRocket + linear interp. | 0.6651 | 0.1613 | 0.6375 | 0.6290 |
| mnar | 0.8000 | MiniRocket + zero fill | 0.6331 | 0.1727 | 0.6054 | 0.5961 |
| mnar | 0.8000 | MiniRocket + mean fill | 0.6105 | 0.1742 | 0.5800 | 0.5711 |
| mnar | 0.8000 | MiniRocket + LOCF | 0.6428 | 0.1703 | 0.6162 | 0.6078 |
| mnar | 0.8000 | MiniRocket + kNN impute | 0.6325 | 0.1795 | 0.6051 | 0.5927 |
| mnar | 0.8000 | MultiRocket + linear interp. | 0.6786 | 0.1688 | 0.6535 | 0.6468 |
| mnar | 0.8000 | Hydra-MultiRocket + linear interp. | 0.6751 | 0.1617 | 0.6494 | 0.6429 |
| mnar | 0.8000 | Native masked MiniRocket (group-mean) | 0.6648 | 0.1681 | 0.6355 | 0.6260 |
| mnar | 0.8000 | LightGBM (native NaN) | 0.5509 | 0.1983 | 0.5214 | 0.5059 |
| mnar | 0.8000 | 1-NN ED + linear interp. | 0.5313 | 0.1827 | 0.5113 | 0.5018 |
| mnar | 0.8000 | w/o weighting (γ=0) | 0.6692 | 0.1604 | 0.6417 | 0.6329 |


## S6 GRU-D on the restricted UCR subset (E2): mean accuracy


| mechanism | test_rate | method | mean | std | count |
|:--------------------|----------:|----------:|----------:|----------:|----------:|
| mcar | 0.5000 | AeonMiniRocket+linear | 0.9638 | 0.0362 | 5 |
| mcar | 0.5000 | GRU-D | 0.4868 | 0.2364 | 5 |
| mcar | 0.5000 | MissRocket | 0.9575 | 0.0390 | 5 |


## S7 GRU-D comparison statistics (E2)


| mechanism | rate | baseline | n_datasets | mean_diff | median_diff | ci95_low | ci95_high | wins | ties | losses | rank_biserial | p_value | p_holm |
|:--------------------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| mcar | 0.5000 | AeonMiniRocket+linear | 5 | -0.0064 | -0.0010 | -0.0134 | 0.0002 | 1 | 1 | 3 | -0.6000 | 0.375 | 0.375 |
| mcar | 0.5000 | GRU-D | 5 | 0.4707 | 0.5511 | 0.2797 | 0.6617 | 5 | 0 | 0 | 1.0000 | 0.062 | 0.125 |


## S8 Efficiency of all methods (E1, seed 0)


| method | median_total_s | mean_total_s | total_cpu_h | median_features |
|:--------------------|----------:|----------:|----------:|----------:|
| 1-NN ED + linear interp. | 0.0117 | 0.0208 | 0.0047 | 301.0000 |
| MiniRocket + LOCF | 0.3014 | 0.4342 | 0.0988 | 9996.0000 |
| MiniRocket + linear interp. | 0.3037 | 0.4500 | 0.1024 | 9996.0000 |
| MiniRocket + mean fill | 0.3059 | 0.4409 | 0.1003 | 9996.0000 |
| MiniRocket + zero fill | 0.3098 | 0.4330 | 0.0985 | 9996.0000 |
| MiniRocket + kNN impute | 0.5026 | 0.9495 | 0.2160 | 9996.0000 |
| Native masked MiniRocket (group-mean) | 0.5398 | 1.0084 | 0.2294 | 9996.0000 |
| LightGBM (native NaN) | 0.6922 | 2.2679 | 0.5159 | 301.0000 |
| MissRocket (proposed) | 1.2408 | 2.6217 | 0.5964 | 9996.0000 |
| w/o weighting (γ=0) | 1.2472 | 2.5656 | 0.5837 | 9996.0000 |
| MultiRocket + linear interp. | 2.5610 | 4.1015 | 0.9331 | 49728.0000 |
| Hydra-MultiRocket + linear interp. | 4.1127 | 8.5976 | 1.9559 | 55872.0000 |


## S9 Choice of γ by the leave-one-out selection variant (E3)


| mechanism | test_rate | 1.0 |
|:--------------------|----------:|----------:|
| block | 0.2000 | 1.0000 |
| block | 0.5000 | 1.0000 |
| block | 0.8000 | 1.0000 |
| mcar | 0.2000 | 1.0000 |
| mcar | 0.5000 | 1.0000 |
| mcar | 0.8000 | 1.0000 |
| mnar | 0.2000 | 1.0000 |
| mnar | 0.5000 | 1.0000 |
| mnar | 0.8000 | 1.0000 |


## S10 Sensitivity analysis (E7)


| parameter | value | mechanism | accuracy |
|:--------------------|----------:|----------:|----------:|
| gamma | 0.0000 | block | 0.6423 |
| gamma | 0.0000 | mcar | 0.8050 |
| gamma | 0.2500 | block | 0.6718 |
| gamma | 0.2500 | mcar | 0.8064 |
| gamma | 0.5000 | block | 0.6795 |
| gamma | 0.5000 | mcar | 0.8053 |
| gamma | 1.0000 | block | 0.6735 |
| gamma | 1.0000 | mcar | 0.7989 |
| gamma | 2.0000 | block | 0.6665 |
| gamma | 2.0000 | mcar | 0.7917 |
| gamma | 4.0000 | block | 0.6505 |
| gamma | 4.0000 | mcar | 0.7644 |
| num_features_gamma1 | 2500.0000 | block | 0.6670 |
| num_features_gamma1 | 2500.0000 | mcar | 0.7947 |
| num_features_gamma1 | 5000.0000 | block | 0.6756 |
| num_features_gamma1 | 5000.0000 | mcar | 0.7923 |
| num_features_gamma1 | 10000.0000 | block | 0.6735 |
| num_features_gamma1 | 10000.0000 | mcar | 0.7989 |
| num_features_gamma1 | 20000.0000 | block | 0.6730 |
| num_features_gamma1 | 20000.0000 | mcar | 0.7961 |
| num_features_gamma0 | 2500.0000 | block | 0.6385 |
| num_features_gamma0 | 2500.0000 | mcar | 0.8009 |
| num_features_gamma0 | 5000.0000 | block | 0.6427 |
| num_features_gamma0 | 5000.0000 | mcar | 0.8021 |
| num_features_gamma0 | 10000.0000 | block | 0.6423 |
| num_features_gamma0 | 10000.0000 | mcar | 0.8050 |
| num_features_gamma0 | 20000.0000 | block | 0.6461 |
| num_features_gamma0 | 20000.0000 | mcar | 0.8017 |


## S11 Raw results

All per-run results are provided as Online Resource 2 (ESM_2.csv). Columns: dataset, mechanism, train_rate, test_rate, seed, method, accuracy, balanced_accuracy, macro_f1, auroc, auprc, fit_s, predict_s, n_features, train_obs_frac, test_obs_frac, selected_gamma, selected_mask, status, timestamp, experiment.