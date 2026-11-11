| mechanism   |   rate | method                                |   mean_accuracy |   std_accuracy |   mean_balanced_accuracy |   mean_macro_f1 |
|:------------|-------:|:--------------------------------------|----------------:|---------------:|-------------------------:|----------------:|
| block       | 0.5000 | MissRocket (proposed)                 |          0.8115 |         0.1204 |                   0.8135 |          0.8112 |
| block       | 0.5000 | MiniRocket + linear interp.           |          0.7628 |         0.1701 |                   0.7655 |          0.7617 |
| block       | 0.5000 | MiniRocket + zero fill                |          0.7373 |         0.0952 |                   0.7401 |          0.7361 |
| block       | 0.5000 | MiniRocket + mean fill                |          0.6726 |         0.1891 |                   0.6759 |          0.6701 |
| block       | 0.5000 | MiniRocket + LOCF                     |          0.7419 |         0.1814 |                   0.7403 |          0.7399 |
| block       | 0.5000 | MiniRocket + kNN impute               |          0.9612 |         0.0340 |                   0.9612 |          0.9612 |
| block       | 0.5000 | MultiRocket + linear interp.          |          0.7899 |         0.1598 |                   0.7917 |          0.7896 |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.7902 |         0.1600 |                   0.7920 |          0.7899 |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |          0.8085 |         0.0999 |                   0.8114 |          0.8079 |
| block       | 0.5000 | LightGBM (native NaN)                 |          0.8035 |         0.0536 |                   0.8005 |          0.8002 |
| block       | 0.5000 | 1-NN ED + linear interp.              |          0.7470 |         0.0575 |                   0.7465 |          0.7354 |
| block       | 0.5000 | w/o weighting (γ=0)                   |          0.7550 |         0.1938 |                   0.7551 |          0.7546 |
| mcar        | 0.5000 | MissRocket (proposed)                 |          0.9396 |         0.0576 |                   0.9395 |          0.9395 |
| mcar        | 0.5000 | MiniRocket + linear interp.           |          0.9339 |         0.0676 |                   0.9338 |          0.9338 |
| mcar        | 0.5000 | MiniRocket + zero fill                |          0.7370 |         0.1875 |                   0.7404 |          0.7341 |
| mcar        | 0.5000 | MiniRocket + mean fill                |          0.6918 |         0.2395 |                   0.6941 |          0.6892 |
| mcar        | 0.5000 | MiniRocket + LOCF                     |          0.9051 |         0.0637 |                   0.9042 |          0.9047 |
| mcar        | 0.5000 | MiniRocket + kNN impute               |          0.9600 |         0.0360 |                   0.9600 |          0.9601 |
| mcar        | 0.5000 | MultiRocket + linear interp.          |          0.9363 |         0.0622 |                   0.9363 |          0.9361 |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.9370 |         0.0613 |                   0.9369 |          0.9368 |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |          0.8145 |         0.1226 |                   0.8131 |          0.8132 |
| mcar        | 0.5000 | LightGBM (native NaN)                 |          0.7917 |         0.0782 |                   0.7896 |          0.7876 |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |          0.8541 |         0.0653 |                   0.8522 |          0.8477 |
| mcar        | 0.5000 | w/o weighting (γ=0)                   |          0.9329 |         0.0656 |                   0.9329 |          0.9328 |
| mnar        | 0.5000 | MissRocket (proposed)                 |          0.9151 |         0.0975 |                   0.9151 |          0.9149 |
| mnar        | 0.5000 | MiniRocket + linear interp.           |          0.8917 |         0.1001 |                   0.8925 |          0.8915 |
| mnar        | 0.5000 | MiniRocket + zero fill                |          0.8164 |         0.1216 |                   0.8185 |          0.8161 |
| mnar        | 0.5000 | MiniRocket + mean fill                |          0.7339 |         0.1549 |                   0.7365 |          0.7321 |
| mnar        | 0.5000 | MiniRocket + LOCF                     |          0.8316 |         0.0705 |                   0.8322 |          0.8312 |
| mnar        | 0.5000 | MiniRocket + kNN impute               |          0.9114 |         0.0483 |                   0.9105 |          0.9112 |
| mnar        | 0.5000 | MultiRocket + linear interp.          |          0.8735 |         0.0813 |                   0.8725 |          0.8730 |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.8851 |         0.0885 |                   0.8833 |          0.8844 |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |          0.8698 |         0.0714 |                   0.8696 |          0.8695 |
| mnar        | 0.5000 | LightGBM (native NaN)                 |          0.8399 |         0.0384 |                   0.8379 |          0.8377 |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |          0.7020 |         0.0570 |                   0.7049 |          0.6897 |
| mnar        | 0.5000 | w/o weighting (γ=0)                   |          0.8885 |         0.1005 |                   0.8893 |          0.8882 |