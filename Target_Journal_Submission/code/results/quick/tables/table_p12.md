| method                                |   auroc_mean |   auroc_std |   auprc_mean |   auprc_std |   time_s_mean |   n_seeds |
|:--------------------------------------|-------------:|------------:|-------------:|------------:|--------------:|----------:|
| GRU-D                                 |       0.7966 |         nan |       0.4137 |         nan |      147.7730 |         1 |
| LightGBM (native NaN)                 |       0.7592 |         nan |       0.4351 |         nan |        3.0024 |         1 |
| MissRocket (proposed)                 |       0.7249 |         nan |       0.2892 |         nan |        2.0671 |         1 |
| w/o weighting (γ=0)                   |       0.7192 |         nan |       0.3012 |         nan |        2.1374 |         1 |
| γ, mask selected by LOO               |       0.7102 |         nan |       0.2848 |         nan |        5.6848 |         1 |
| Native masked MiniRocket (group-mean) |       0.6715 |         nan |       0.2345 |         nan |        1.2964 |         1 |