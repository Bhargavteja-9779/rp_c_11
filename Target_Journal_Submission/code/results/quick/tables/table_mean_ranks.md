| mechanism   |   rate | method                                |   mean_rank |
|:------------|-------:|:--------------------------------------|------------:|
| block       | 0.5000 | MiniRocket + kNN impute               |      1.0000 |
| block       | 0.5000 | MissRocket (proposed)                 |      4.1667 |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    |      4.6667 |
| block       | 0.5000 | MultiRocket + linear interp.          |      5.0000 |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |      5.0000 |
| block       | 0.5000 | LightGBM (native NaN)                 |      5.3333 |
| block       | 0.5000 | MiniRocket + linear interp.           |      7.0000 |
| block       | 0.5000 | 1-NN ED + linear interp.              |      7.3333 |
| block       | 0.5000 | MiniRocket + zero fill                |      8.1667 |
| block       | 0.5000 | MiniRocket + LOCF                     |      8.1667 |
| block       | 0.5000 | MiniRocket + mean fill                |     10.1667 |
| mcar        | 0.5000 | MiniRocket + kNN impute               |      1.6667 |
| mcar        | 0.5000 | MissRocket (proposed)                 |      3.0000 |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |      3.3333 |
| mcar        | 0.5000 | MiniRocket + linear interp.           |      3.6667 |
| mcar        | 0.5000 | MultiRocket + linear interp.          |      3.6667 |
| mcar        | 0.5000 | MiniRocket + LOCF                     |      7.0000 |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |      7.3333 |
| mcar        | 0.5000 | LightGBM (native NaN)                 |      8.0000 |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |      8.6667 |
| mcar        | 0.5000 | MiniRocket + zero fill                |      9.3333 |
| mcar        | 0.5000 | MiniRocket + mean fill                |     10.3333 |
| mnar        | 0.5000 | MissRocket (proposed)                 |      2.6667 |
| mnar        | 0.5000 | MiniRocket + kNN impute               |      3.8333 |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |      3.8333 |
| mnar        | 0.5000 | MultiRocket + linear interp.          |      4.5000 |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |      4.5000 |
| mnar        | 0.5000 | MiniRocket + linear interp.           |      5.1667 |
| mnar        | 0.5000 | MiniRocket + zero fill                |      6.6667 |
| mnar        | 0.5000 | LightGBM (native NaN)                 |      6.8333 |
| mnar        | 0.5000 | MiniRocket + LOCF                     |      7.6667 |
| mnar        | 0.5000 | MiniRocket + mean fill                |      9.6667 |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |     10.6667 |