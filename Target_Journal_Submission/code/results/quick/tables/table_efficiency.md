| method                                |   median_total_s |   mean_total_s |   total_cpu_h |   median_features |
|:--------------------------------------|-----------------:|---------------:|--------------:|------------------:|
| 1-NN ED + linear interp.              |            0.007 |          0.006 |         0.000 |            60.000 |
| MiniRocket + linear interp.           |            0.122 |          0.213 |         0.001 |          9996.000 |
| MiniRocket + mean fill                |            0.131 |          0.126 |         0.000 |          9996.000 |
| MiniRocket + LOCF                     |            0.132 |          0.126 |         0.000 |          9996.000 |
| Native masked MiniRocket (group-mean) |            0.132 |          0.730 |         0.002 |          9996.000 |
| MiniRocket + zero fill                |            0.141 |          0.118 |         0.000 |          9996.000 |
| LightGBM (native NaN)                 |            0.156 |          0.295 |         0.001 |            60.000 |
| MiniRocket + kNN impute               |            0.162 |          0.172 |         0.000 |          9996.000 |
| w/o weighting (γ=0)                   |            0.243 |          0.256 |         0.001 |          9996.000 |
| MissRocket (proposed)                 |            0.258 |          1.411 |         0.004 |          9996.000 |
| MultiRocket + linear interp.          |            0.938 |          2.527 |         0.006 |         49728.000 |
| Hydra-MultiRocket + linear interp.    |            0.942 |          1.149 |         0.003 |         52800.000 |