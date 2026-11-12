| method                                |   median_total_s |   mean_total_s |   total_cpu_h |   median_features |
|:--------------------------------------|-----------------:|---------------:|--------------:|------------------:|
| 1-NN ED + linear interp.              |            0.003 |          0.004 |         0.000 |           150.000 |
| MiniRocket + linear interp.           |            0.098 |          0.228 |         0.001 |          9996.000 |
| MiniRocket + mean fill                |            0.116 |          0.121 |         0.000 |          9996.000 |
| MiniRocket + LOCF                     |            0.131 |          0.126 |         0.000 |          9996.000 |
| MiniRocket + zero fill                |            0.132 |          0.124 |         0.000 |          9996.000 |
| MiniRocket + kNN impute               |            0.158 |          0.175 |         0.000 |          9996.000 |
| LightGBM (native NaN)                 |            0.198 |          0.478 |         0.001 |           150.000 |
| Native masked MiniRocket (group-mean) |            0.233 |          0.820 |         0.002 |          9996.000 |
| w/o weighting (γ=0)                   |            0.312 |          0.340 |         0.001 |          9996.000 |
| MissRocket (proposed)                 |            0.338 |          1.625 |         0.004 |          9996.000 |
| MultiRocket + linear interp.          |            0.516 |          0.581 |         0.001 |         49728.000 |
| Hydra-MultiRocket + linear interp.    |            1.000 |          0.962 |         0.002 |         54848.000 |