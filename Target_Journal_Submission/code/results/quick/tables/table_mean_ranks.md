| mechanism   |   rate | method                                |   mean_rank |
|:------------|-------:|:--------------------------------------|------------:|
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    |      2.0000 |
| block       | 0.5000 | MiniRocket + kNN impute               |      2.3333 |
| block       | 0.5000 | MissRocket (proposed)                 |      2.8333 |
| block       | 0.5000 | MultiRocket + linear interp.          |      3.1667 |
| block       | 0.5000 | MiniRocket + linear interp.           |      5.3333 |
| block       | 0.5000 | 1-NN ED + linear interp.              |      6.8333 |
| block       | 0.5000 | MiniRocket + LOCF                     |      7.0000 |
| block       | 0.5000 | LightGBM (native NaN)                 |      7.3333 |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |      8.8333 |
| block       | 0.5000 | MiniRocket + zero fill                |     10.0000 |
| block       | 0.5000 | MiniRocket + mean fill                |     10.3333 |
| mcar        | 0.5000 | MultiRocket + linear interp.          |      2.1667 |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |      2.6667 |
| mcar        | 0.5000 | MiniRocket + LOCF                     |      4.1667 |
| mcar        | 0.5000 | MiniRocket + kNN impute               |      4.3333 |
| mcar        | 0.5000 | MiniRocket + linear interp.           |      4.6667 |
| mcar        | 0.5000 | MissRocket (proposed)                 |      4.8333 |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |      6.1667 |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |      7.8333 |
| mcar        | 0.5000 | MiniRocket + zero fill                |      9.0000 |
| mcar        | 0.5000 | MiniRocket + mean fill                |      9.6667 |
| mcar        | 0.5000 | LightGBM (native NaN)                 |     10.5000 |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |      2.5000 |
| mnar        | 0.5000 | MultiRocket + linear interp.          |      3.0000 |
| mnar        | 0.5000 | MissRocket (proposed)                 |      3.3333 |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |      5.1667 |
| mnar        | 0.5000 | MiniRocket + linear interp.           |      5.5000 |
| mnar        | 0.5000 | MiniRocket + mean fill                |      6.3333 |
| mnar        | 0.5000 | MiniRocket + kNN impute               |      6.8333 |
| mnar        | 0.5000 | MiniRocket + zero fill                |      7.0000 |
| mnar        | 0.5000 | MiniRocket + LOCF                     |      7.3333 |
| mnar        | 0.5000 | LightGBM (native NaN)                 |      9.5000 |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |      9.5000 |