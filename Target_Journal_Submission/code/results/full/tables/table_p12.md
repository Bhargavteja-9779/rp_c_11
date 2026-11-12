| method                                |   auroc_mean |   auroc_std |   auprc_mean |   auprc_std |   time_s_mean |   n_seeds |
|:--------------------------------------|-------------:|------------:|-------------:|------------:|--------------:|----------:|
| GRU-D                                 |       0.8599 |         nan |       0.5403 |         nan |     1148.4996 |         1 |
| LightGBM (native NaN)                 |       0.8457 |         nan |       0.5215 |         nan |       12.3801 |         1 |
| γ, mask selected by LOO               |       0.8061 |         nan |       0.4906 |         nan |      373.4262 |         1 |
| w/o weighting (γ=0)                   |       0.8061 |         nan |       0.4906 |         nan |       65.2329 |         1 |
| MissRocket (proposed)                 |       0.8027 |         nan |       0.4889 |         nan |       65.5333 |         1 |
| Native masked MiniRocket (group-mean) |       0.7845 |         nan |       0.4514 |         nan |       53.3445 |         1 |