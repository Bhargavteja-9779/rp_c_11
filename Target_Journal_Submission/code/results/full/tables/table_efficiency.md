| method                                |   median_total_s |   mean_total_s |   total_cpu_h |   median_features |
|:--------------------------------------|-----------------:|---------------:|--------------:|------------------:|
| 1-NN ED + linear interp.              |            0.012 |          0.021 |         0.005 |           301.000 |
| MiniRocket + LOCF                     |            0.301 |          0.434 |         0.099 |          9996.000 |
| MiniRocket + linear interp.           |            0.304 |          0.450 |         0.102 |          9996.000 |
| MiniRocket + mean fill                |            0.306 |          0.441 |         0.100 |          9996.000 |
| MiniRocket + zero fill                |            0.310 |          0.433 |         0.099 |          9996.000 |
| MiniRocket + kNN impute               |            0.503 |          0.950 |         0.216 |          9996.000 |
| Native masked MiniRocket (group-mean) |            0.540 |          1.008 |         0.229 |          9996.000 |
| LightGBM (native NaN)                 |            0.692 |          2.268 |         0.516 |           301.000 |
| MissRocket (proposed)                 |            1.241 |          2.622 |         0.596 |          9996.000 |
| w/o weighting (γ=0)                   |            1.247 |          2.566 |         0.584 |          9996.000 |
| MultiRocket + linear interp.          |            2.561 |          4.102 |         0.933 |         49728.000 |
| Hydra-MultiRocket + linear interp.    |            4.113 |          8.598 |         1.956 |         55872.000 |