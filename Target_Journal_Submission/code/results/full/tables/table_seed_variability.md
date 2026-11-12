| mechanism   |   rate | baseline                              |       0 |        1 |   sd_over_seeds | sign_agreement   |
|:------------|-------:|:--------------------------------------|--------:|---------:|----------------:|:-----------------|
| block       | 0.2000 | 1-NN ED + linear interp.              |  0.1400 | nan      |        nan      | False            |
| block       | 0.2000 | Hydra-MultiRocket + linear interp.    | -0.0333 | nan      |        nan      | False            |
| block       | 0.2000 | LightGBM (native NaN)                 |  0.0600 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + LOCF                     |  0.0000 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + kNN impute               |  0.0267 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + linear interp.           | -0.0200 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + mean fill                |  0.1067 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + zero fill                |  0.0333 | nan      |        nan      | False            |
| block       | 0.2000 | MultiRocket + linear interp.          | -0.0333 | nan      |        nan      | False            |
| block       | 0.2000 | Native masked MiniRocket (group-mean) |  0.0400 | nan      |        nan      | False            |
| block       | 0.2000 | w/o weighting (γ=0)                   | -0.0200 | nan      |        nan      | False            |
| block       | 0.5000 | 1-NN ED + linear interp.              |  0.0667 | nan      |        nan      | False            |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    | -0.1133 | nan      |        nan      | False            |
| block       | 0.5000 | LightGBM (native NaN)                 | -0.0600 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + LOCF                     | -0.0133 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + kNN impute               | -0.1800 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + linear interp.           | -0.0467 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + mean fill                |  0.0933 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + zero fill                |  0.0867 | nan      |        nan      | False            |
| block       | 0.5000 | MultiRocket + linear interp.          | -0.1133 | nan      |        nan      | False            |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |  0.1267 | nan      |        nan      | False            |
| block       | 0.5000 | w/o weighting (γ=0)                   | -0.0200 | nan      |        nan      | False            |
| block       | 0.8000 | 1-NN ED + linear interp.              |  0.0333 | nan      |        nan      | False            |
| block       | 0.8000 | Hydra-MultiRocket + linear interp.    | -0.0133 | nan      |        nan      | False            |
| block       | 0.8000 | LightGBM (native NaN)                 |  0.0133 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + LOCF                     |  0.1067 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + kNN impute               | -0.0533 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + linear interp.           |  0.0600 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + mean fill                |  0.0533 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + zero fill                |  0.0267 | nan      |        nan      | False            |
| block       | 0.8000 | MultiRocket + linear interp.          | -0.0133 | nan      |        nan      | False            |
| block       | 0.8000 | Native masked MiniRocket (group-mean) |  0.0200 | nan      |        nan      | False            |
| block       | 0.8000 | w/o weighting (γ=0)                   |  0.0533 | nan      |        nan      | False            |
| mcar        | 0.2000 | 1-NN ED + linear interp.              |  0.1733 | nan      |        nan      | False            |
| mcar        | 0.2000 | Hydra-MultiRocket + linear interp.    |  0.0000 |  -0.0067 |          0.0047 | False            |
| mcar        | 0.2000 | LightGBM (native NaN)                 |  0.0533 | nan      |        nan      | False            |
| mcar        | 0.2000 | MiniRocket + LOCF                     |  0.0000 |  -0.0067 |          0.0047 | False            |
| mcar        | 0.2000 | MiniRocket + kNN impute               |  0.0133 |   0.0267 |          0.0094 | True             |
| mcar        | 0.2000 | MiniRocket + linear interp.           |  0.0000 |  -0.0067 |          0.0047 | False            |
| mcar        | 0.2000 | MiniRocket + mean fill                |  0.0933 |   0.0267 |          0.0471 | True             |
| mcar        | 0.2000 | MiniRocket + zero fill                |  0.0267 |   0.0000 |          0.0189 | False            |
| mcar        | 0.2000 | MultiRocket + linear interp.          |  0.0000 |  -0.0067 |          0.0047 | False            |
| mcar        | 0.2000 | Native masked MiniRocket (group-mean) |  0.0000 | nan      |        nan      | False            |
| mcar        | 0.2000 | w/o weighting (γ=0)                   |  0.0000 |  -0.0067 |          0.0047 | False            |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |  0.1667 | nan      |        nan      | False            |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |  0.0067 | nan      |        nan      | False            |
| mcar        | 0.5000 | LightGBM (native NaN)                 |  0.1733 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + LOCF                     |  0.0067 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + kNN impute               |  0.0933 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + linear interp.           |  0.0000 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + mean fill                |  0.1267 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + zero fill                |  0.0867 | nan      |        nan      | False            |
| mcar        | 0.5000 | MultiRocket + linear interp.          |  0.0067 | nan      |        nan      | False            |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |  0.1200 | nan      |        nan      | False            |
| mcar        | 0.5000 | w/o weighting (γ=0)                   |  0.0000 | nan      |        nan      | False            |
| mcar        | 0.8000 | 1-NN ED + linear interp.              |  0.1467 | nan      |        nan      | False            |
| mcar        | 0.8000 | Hydra-MultiRocket + linear interp.    | -0.0200 | nan      |        nan      | False            |
| mcar        | 0.8000 | LightGBM (native NaN)                 |  0.4667 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + LOCF                     |  0.0133 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + kNN impute               |  0.1600 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + linear interp.           | -0.0067 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + mean fill                |  0.3267 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + zero fill                |  0.2267 | nan      |        nan      | False            |
| mcar        | 0.8000 | MultiRocket + linear interp.          | -0.0200 | nan      |        nan      | False            |
| mcar        | 0.8000 | Native masked MiniRocket (group-mean) |  0.2200 | nan      |        nan      | False            |
| mcar        | 0.8000 | w/o weighting (γ=0)                   | -0.0133 | nan      |        nan      | False            |
| mnar        | 0.2000 | 1-NN ED + linear interp.              |  0.2200 | nan      |        nan      | False            |
| mnar        | 0.2000 | Hydra-MultiRocket + linear interp.    | -0.0400 | nan      |        nan      | False            |
| mnar        | 0.2000 | LightGBM (native NaN)                 |  0.0067 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + LOCF                     |  0.0000 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + kNN impute               |  0.0267 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + linear interp.           | -0.0267 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + mean fill                |  0.1067 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + zero fill                |  0.0867 | nan      |        nan      | False            |
| mnar        | 0.2000 | MultiRocket + linear interp.          | -0.0400 | nan      |        nan      | False            |
| mnar        | 0.2000 | Native masked MiniRocket (group-mean) |  0.0400 | nan      |        nan      | False            |
| mnar        | 0.2000 | w/o weighting (γ=0)                   | -0.0200 | nan      |        nan      | False            |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |  0.2400 | nan      |        nan      | False            |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |  0.0133 | nan      |        nan      | False            |
| mnar        | 0.5000 | LightGBM (native NaN)                 |  0.1333 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + LOCF                     |  0.0467 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + kNN impute               |  0.1133 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + linear interp.           |  0.0667 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + mean fill                |  0.2133 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + zero fill                |  0.1933 | nan      |        nan      | False            |
| mnar        | 0.5000 | MultiRocket + linear interp.          |  0.0200 | nan      |        nan      | False            |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |  0.0733 | nan      |        nan      | False            |
| mnar        | 0.5000 | w/o weighting (γ=0)                   |  0.0533 | nan      |        nan      | False            |
| mnar        | 0.8000 | 1-NN ED + linear interp.              |  0.1133 | nan      |        nan      | False            |
| mnar        | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0800 | nan      |        nan      | False            |
| mnar        | 0.8000 | LightGBM (native NaN)                 |  0.1200 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + LOCF                     |  0.1133 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + kNN impute               |  0.0867 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + linear interp.           |  0.1333 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + mean fill                |  0.0667 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + zero fill                |  0.0600 | nan      |        nan      | False            |
| mnar        | 0.8000 | MultiRocket + linear interp.          |  0.0800 | nan      |        nan      | False            |
| mnar        | 0.8000 | Native masked MiniRocket (group-mean) |  0.0133 | nan      |        nan      | False            |
| mnar        | 0.8000 | w/o weighting (γ=0)                   |  0.1133 | nan      |        nan      | False            |