## 6 Results

### 6.1 Main comparison (RQ1)

@tab:main reports mean test accuracy over the {{N_CONF}} confirmatory datasets for every mechanism and rate. Paired comparisons with the strongest competitors are given in @tab:stats, and pooled comparisons in @tab:pooled. @fig:rate shows accuracy against the missing rate.

{#tab:main} Mean test accuracy over {{N_CONF}} UCR datasets (seed 0) under MCAR, block (contiguous-gap) and MNAR (self-masking) missingness at 20%, 50% and 80% missing values. Mean rank is computed among the eleven methods of the main comparison (the γ=0 ablation is excluded). Best value per column in bold

{{TABLE:main_accuracy}}

Averaged over the nine conditions, MissRocket attains the highest mean accuracy and the best mean rank. The differences are condition-specific, however.

**Long gaps.** Under block missingness, MissRocket improves on MiniRocket with linear interpolation at every rate:
- 20%: {{Q:table_main_statistics;mechanism=block;rate=0.2;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp;
- 50%: {{Q:table_main_statistics;mechanism=block;rate=0.5;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp;
- 80%: {{Q:table_main_statistics;mechanism=block;rate=0.8;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp;

all with Holm-adjusted p ≤ {{Q:table_main_statistics;mechanism=block;rate=0.2;baseline=MiniRocket + linear interp.;col=p_holm;fmt=f3}}.

At 50% and 80%, MissRocket is also significantly more accurate than MultiRocket and Hydra-MultiRocket after interpolation. Both are considerably more expensive transforms; Section 6.6 gives the costs.

**Value-dependent missingness.** Under MNAR, the gains over MiniRocket with interpolation grow with the missing rate:
- 20%: {{Q:table_main_statistics;mechanism=mnar;rate=0.2;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_main_statistics;mechanism=mnar;rate=0.2;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}};
- 50%: {{Q:table_main_statistics;mechanism=mnar;rate=0.5;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_main_statistics;mechanism=mnar;rate=0.5;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}};
- 80%: {{Q:table_main_statistics;mechanism=mnar;rate=0.8;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_main_statistics;mechanism=mnar;rate=0.8;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}}.

**Scattered gaps.** Under MCAR, MissRocket is not significantly different from MiniRocket with interpolation at any rate: the mean differences are {{Q:table_main_statistics;mechanism=mcar;rate=0.2;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}}, {{Q:table_main_statistics;mechanism=mcar;rate=0.5;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} and {{Q:table_main_statistics;mechanism=mcar;rate=0.8;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp. At 20% MCAR it is slightly but significantly *less* accurate than MultiRocket ({{Q:table_main_statistics;mechanism=mcar;rate=0.2;baseline=MultiRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_main_statistics;mechanism=mcar;rate=0.2;baseline=MultiRocket + linear interp.;col=p_holm;fmt=p}}) and than Hydra-MultiRocket ({{Q:table_main_statistics;mechanism=mcar;rate=0.2;baseline=Hydra-MultiRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_main_statistics;mechanism=mcar;rate=0.2;baseline=Hydra-MultiRocket + linear interp.;col=p_holm;fmt=p}}).

{#tab:stats} Paired comparison of MissRocket with the strongest competitors and with its own unweighted ablation (γ=0), per condition. Δ is the mean accuracy difference in percentage points (positive favours MissRocket), with a dataset-level bootstrap 95% CI; W/T/L are wins/ties/losses over datasets; r_rb is the matched-pairs rank-biserial correlation; p is the two-sided Wilcoxon signed-rank test, Holm-corrected within each condition over the ten baselines (γ=0: separate single comparison)

{{TABLE:main_statistics}}

**Cross-series kNN imputation.** kNN imputation followed by MiniRocket behaves very differently by mechanism. It is the most accurate method under block missingness. At 50% blocks it is {{Q:table_main_statistics;mechanism=block;rate=0.5;baseline=MiniRocket + kNN impute;col=mean_diff;fmt=ppabs}} pp better than MissRocket (p (Holm) {{Q:table_main_statistics;mechanism=block;rate=0.5;baseline=MiniRocket + kNN impute;col=p_holm;fmt=p}}). Under MCAR and MNAR, by contrast, it is substantially worse; at 80% MCAR, MissRocket is {{Q:table_main_statistics;mechanism=mcar;rate=0.8;baseline=MiniRocket + kNN impute;col=mean_diff;fmt=pp}} pp better. Exploiting aligned training series therefore pays off when whole segments are missing, but it is harmful when the gaps are short and scattered.

**Native estimation and generic learners.**
- The native group-mean estimator is significantly worse than MissRocket in every condition. This confirms, on held-out data, the development-set observation and Proposition 2: an unbiased but high-variance response estimate loses to interpolation.
- LightGBM with native missing-value handling, and 1-NN after interpolation, are far less accurate than every ROCKET-family pipeline.
- Zero and mean filling are the worst gap fillers for MiniRocket. This matters because zero filling is common in practice.

{#tab:pooled} Pooled comparison over all nine conditions (per-dataset mean accuracy over conditions; {{N_CONF}} datasets)

{{TABLE:pooled}}

Pooled over all conditions, MissRocket is more accurate than MiniRocket with interpolation by {{Q:table_pooled_statistics;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp (95% CI {{Q:table_pooled_statistics;baseline=MiniRocket + linear interp.;col=ci95_low;fmt=pp}} to {{Q:table_pooled_statistics;baseline=MiniRocket + linear interp.;col=ci95_high;fmt=pp}}; {{Q:table_pooled_statistics;baseline=MiniRocket + linear interp.;col=wins;fmt=int}} wins and {{Q:table_pooled_statistics;baseline=MiniRocket + linear interp.;col=losses;fmt=int}} losses; p (Holm) {{Q:table_pooled_statistics;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}}).

The pooled differences from MultiRocket ({{Q:table_pooled_statistics;baseline=MultiRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_pooled_statistics;baseline=MultiRocket + linear interp.;col=p_holm;fmt=p}}) and from Hydra-MultiRocket ({{Q:table_pooled_statistics;baseline=Hydra-MultiRocket + linear interp.;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_pooled_statistics;baseline=Hydra-MultiRocket + linear interp.;col=p_holm;fmt=p}}) are not statistically significant. We therefore do not claim that MissRocket outperforms these stronger transforms overall. What the data show is that observed-tap weighting lets the cheapest member of the family match them on average, and beat them when gaps are long or missingness depends on the values.

![](../code/results/full/figures/Fig_accuracy_vs_rate.png){width=16.5cm}

{#fig:rate} Mean accuracy over {{N_CONF}} datasets as a function of the missing rate for each mechanism (seed 0)

![](../code/results/full/figures/Fig_paired_differences.png){width=16.5cm}

{#fig:diff} Distribution over datasets of the accuracy difference between MissRocket and MiniRocket with linear interpolation (percentage points). Boxes show quartiles, whiskers 1.5 IQR, points outliers

### 6.2 Ablation study (RQ2–RQ3)

The ablations were run on a pre-declared random subset of 30 confirmatory datasets, at rate 0.5, for each mechanism (seed 0). @tab:ablation compares MissRocket with each variant. @tab:filler isolates the effect of weighting for each gap filler.

{#tab:ablation} Ablations on 30 datasets at 50% missing values. "acc." is the mean accuracy of the variant; Δ is MissRocket minus the variant in percentage points (positive favours MissRocket), with the Holm-corrected Wilcoxon p-value (family: the twelve comparisons within a mechanism)

{{TABLE:ablation}}

{#tab:filler} Effect of observed-tap weighting (γ=1 vs γ=0) for each gap filler on the same 30 datasets at 50% missing values: mean difference in pp (W/T/L; Holm-corrected p over the twelve filler × mechanism comparisons)

{{TABLE:weighting_by_filler}}

**Weighting is the active component.** Removing it (γ=0) costs {{Q:table_weighting_by_gap_filler;mechanism=block;rate=0.5;gap_filler=linear;col=mean_diff;fmt=ppabs}} pp under block missingness (p (Holm) {{Q:table_weighting_by_gap_filler;mechanism=block;rate=0.5;gap_filler=linear;col=p_holm;fmt=p}}), with {{Q:table_weighting_by_gap_filler;mechanism=block;rate=0.5;gap_filler=linear;col=wins;fmt=int}} of 30 datasets improving. On all {{N_CONF}} datasets and rates the effect is consistent (@tab:stats):
- weighting improves on γ=0 under block missingness at every rate, and under MNAR at 50% and 80%;
- it is neutral under MCAR, except for a small significant loss at 50% ({{Q:table_weighting_vs_unweighted_3seeds;mechanism=mcar;rate=0.5;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_weighting_vs_unweighted_3seeds;mechanism=mcar;rate=0.5;col=p_holm;fmt=p}}).

**The benefit is not tied to linear interpolation.** Weighting also improves LOCF filling under block missingness (@tab:filler). It does *not* improve kNN filling, which does not draw straight lines through gaps and therefore does not produce the fabricated responses of Proposition 3.

**The exponent is not critical.** γ=0.5 and γ=2 are not significantly different from γ=1 in any mechanism. Selecting γ and the mask option on the training set by leave-one-out brings no significant improvement either. This is consistent with the development-set observation that motivated fixing γ=1.

**Missingness-pattern features do not help.** Adding them to MissRocket gives no significant gain under block or MNAR missingness. Under MCAR they are slightly harmful ({{Q:table_ablation_statistics;mechanism=mcar;baseline=+ mask-pattern features;col=mean_diff;fmt=pp}} pp in favour of MissRocket without them, p (Holm) {{Q:table_ablation_statistics;mechanism=mcar;baseline=+ mask-pattern features;col=p_holm;fmt=p}}), where the mask is pure noise.

**The gap filler matters.** Zero filling is far worse than linear filling even with weighting. kNN filling is the strongest filler under block missingness but loses under MCAR and MNAR, mirroring the main comparison.

### 6.3 Robustness to train–test missingness shift (RQ4)

In deployment, a classifier is often trained on curated, complete data and then applied to series with gaps. It may also be trained on data with modest gaps and then face much heavier ones. @tab:shift reports three such shifts, on the 30-dataset subset (seed 0).

{#tab:shift} Accuracy under train–test missing-rate shift (30 datasets). Baseline cells: accuracy (MissRocket minus baseline in pp; W/T/L; Holm-corrected p within the shift condition)

{{TABLE:shift}}

**Block missingness.** Here the shift is most harmful, and MissRocket is markedly more robust. Trained on complete data and tested with 50% block missingness, it reaches {{Q:table_shift;mechanism=block;train_rate=0.0;test_rate=0.5;baseline=MiniRocket + linear interp.;col=proposed_mean;fmt=f3}}, against {{Q:table_shift;mechanism=block;train_rate=0.0;test_rate=0.5;baseline=MiniRocket + linear interp.;col=baseline_mean;fmt=f3}} for MiniRocket with interpolation (p (Holm) {{Q:table_shift;mechanism=block;train_rate=0.0;test_rate=0.5;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}}).

This holds even though the training data contain no missing values, and the reason is the test-time weighting. When the model is trained on complete series, all weights equal one during training. At test time, the weighting removes the fabricated responses inside long gaps, so the pooled features stay closer to the distribution seen in training.

**MCAR.** The shift has little effect on either interpolation-based method. Differences are small: {{Q:table_shift;mechanism=mcar;train_rate=0.0;test_rate=0.5;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp for 0%→50% (not significant) and {{Q:table_shift;mechanism=mcar;train_rate=0.2;test_rate=0.8;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp for 20%→80% (p (Holm) {{Q:table_shift;mechanism=mcar;train_rate=0.2;test_rate=0.8;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}}).

**Native estimators under shift.** The native group-mean estimator and LightGBM degrade severely under MCAR shift. Both rely on statistics whose distribution changes with the missing rate.

### 6.4 External validation: PhysioNet 2012 mortality prediction (RQ5)

{#tab:p12} In-hospital mortality prediction on PhysioNet/CinC 2012 (37 hourly variables over 48 h, 79.7% missing). Train: sets a+b (8,000 stays). Test: set c (4,000 stays). Seed 0. ROCKET-family methods are applied channel-wise (252 features per channel). Time is wall clock for training and prediction on 4 CPU cores

{{TABLE:p12}}

{#tab:p12boot} Paired bootstrap (2,000 resamples of test patients) of the AUROC difference between MissRocket and each method

{{TABLE:p12boot}}

PhysioNet 2012 differs from the UCR experiments in four ways: the series are multivariate, short (48 hourly bins) and very sparse, and their missingness is informative by nature. The results (@tab:p12, @tab:p12boot) are a clear *negative* finding for the random-convolution family.
- **No gain from weighting.** MissRocket (AUROC {{Q:table_p12;method=MissRocket (proposed);col=auroc_mean;fmt=f3}}) does not improve on its unweighted counterpart (AUROC {{Q:table_p12;method=w/o weighting (γ=0);col=auroc_mean;fmt=f3}}). Training-set selection chooses γ=0 without mask features.
- **The deep missing-aware model is best.** GRU-D, which models the mask and the time since the last observation explicitly, attains the highest AUROC ({{Q:table_p12;method=GRU-D;col=auroc_mean;fmt=f3}}) and AUPRC ({{Q:table_p12;method=GRU-D;col=auprc_mean;fmt=f3}}). Its training takes about {{Q:table_p12;method=GRU-D;col=time_s_mean;fmt=int}} s, against {{Q:table_p12;method=MissRocket (proposed);col=time_s_mean;fmt=int}} s for MissRocket.
- **Gradient boosting comes second.** LightGBM on the raw hourly values with native missing-value handling follows (AUROC {{Q:table_p12;method=LightGBM (native NaN);col=auroc_mean;fmt=f3}}).
- **Both beat MissRocket significantly.** The AUROC difference between MissRocket and GRU-D is {{Q:table_p12_bootstrap;baseline=GRU-D;col=auroc_diff_seed_ensemble;fmt=f3}} (95% CI {{Q:table_p12_bootstrap;baseline=GRU-D;col=ci95_low;fmt=f3}} to {{Q:table_p12_bootstrap;baseline=GRU-D;col=ci95_high;fmt=f3}}). Against LightGBM it is {{Q:table_p12_bootstrap;baseline=LightGBM (native NaN);col=auroc_diff_seed_ensemble;fmt=f3}} (95% CI {{Q:table_p12_bootstrap;baseline=LightGBM (native NaN);col=ci95_low;fmt=f3}} to {{Q:table_p12_bootstrap;baseline=LightGBM (native NaN);col=ci95_high;fmt=f3}}).

We attribute the gap to the nature of the data:
- whether, and when, a laboratory value was measured carries information about patient severity;
- the measured *levels* matter more than local temporal shape;
- many channel–patient series are entirely empty.

Models that see the mask and the measured levels directly can exploit each of these; GRU-D does so through its decay mechanism and tree ensembles through their native handling of missing values. Kernels designed to detect shape cannot. Observed-tap weighting addresses fabricated responses inside interpolated gaps, and it cannot add the missingness-pattern and level information that this task needs. We therefore regard MissRocket as suited to *shape-based* classification of sensor-like series with gaps, not as a general method for sparse, irregular clinical records.

### 6.5 Naturally incomplete and variable-length data (RQ5)

{#tab:natural} Accuracy (mean over three seeds) on the 15 UCR datasets that contain native missing values (DodgerLoop*, MelbournePedestrian) or series of unequal length (all others). Variable-length series are right-padded with missing values; "resampling" stretches each series to the common length before MiniRocket

{{TABLE:natural}}

@tab:natural reports the 15 archive datasets that are incomplete by nature, analysed without any simulated missingness. MissRocket is more accurate than MiniRocket with linear interpolation, by {{Q:table_natural_statistics;baseline=MiniRocket + linear interp.;col=mean_diff;fmt=pp}} pp ({{Q:table_natural_statistics;baseline=MiniRocket + linear interp.;col=wins;fmt=int}} wins, {{Q:table_natural_statistics;baseline=MiniRocket + linear interp.;col=losses;fmt=int}} losses; p (Holm) {{Q:table_natural_statistics;baseline=MiniRocket + linear interp.;col=p_holm;fmt=p}}).

For variable-length series, interpolation extends the last observed value over the padded tail. This creates exactly the fabricated, constant windows of Proposition 3, and MissRocket gives them zero weight.

MissRocket is not significantly different from two alternatives:
- the standard resampling approach ({{Q:table_natural_statistics;baseline=MiniRocket + resampling;col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_natural_statistics;baseline=MiniRocket + resampling;col=p_holm;fmt=p}});
- the native group-mean estimator ({{Q:table_natural_statistics;baseline=Native masked MiniRocket (group-mean);col=mean_diff;fmt=pp}} pp, p (Holm) {{Q:table_natural_statistics;baseline=Native masked MiniRocket (group-mean);col=p_holm;fmt=p}}).

The native estimator is competitive here because the missing segment is a single trailing block rather than many interior gaps.

On the four datasets with genuinely missing interior values (DodgerLoopDay, DodgerLoopGame, DodgerLoopWeekend and MelbournePedestrian), the missing fraction is below 1% and all ROCKET-family methods perform similarly. With 15 datasets, these comparisons have limited power.

### 6.6 Computational cost (RQ6)

{#tab:eff} Wall-clock cost per run (fit + predict, including gap filling) on a 4-core CPU without GPU, over all E1 runs (seed 0, nine conditions, {{N_CONF}} datasets). Our MiniRocket implementation (MissRocket, γ=0) is a numba re-implementation; "MiniRocket + …" rows use the optimised reference implementation in aeon

{{TABLE:efficiency}}

@tab:eff summarises the measured costs.

**The weighting is essentially free.** MissRocket and its unweighted counterpart (γ=0) have practically identical run times. The only additions are a per-position count of observed taps and a ten-bin histogram per feature (Section 4.3).

**Implementation, not method, explains the gap to aeon.** Both of our variants are about {{TIME_RATIO_MR_VS_MINI}}× slower than the reference aeon MiniRocket. This reflects the difference between our straightforward numba implementation and aeon's heavily optimised one, not the method; the transform has the same asymptotic cost as MiniRocket.

**Cheaper than the stronger transforms.** Even with this implementation gap, MissRocket is about {{TIME_RATIO_HYDRA_VS_MR}}× faster than Hydra-MultiRocket and uses fewer than a fifth of its features. At the same time, it is at least as accurate on average (Section 6.1).

**Model-based imputation adds cost and memory.** kNN imputation must store the training set and compare every test series with it. Its cost grows with the size of the training set, whereas MissRocket processes each series independently.

GRU-D, which needs iterative training with early stopping, is reported separately in Section 6.7.
