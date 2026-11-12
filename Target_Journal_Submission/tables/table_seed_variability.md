| mechanism   |   rate | baseline                              |       0 |        1 |   sd_over_seeds | sign_agreement   |
|:------------|-------:|:--------------------------------------|--------:|---------:|----------------:|:-----------------|
| block       | 0.2000 | 1-NN ED + linear interp.              |  0.1490 | nan      |        nan      | False            |
| block       | 0.2000 | Hydra-MultiRocket + linear interp.    | -0.0156 | nan      |        nan      | False            |
| block       | 0.2000 | LightGBM (native NaN)                 |  0.0689 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + LOCF                     |  0.0043 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + kNN impute               | -0.0067 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + linear interp.           |  0.0065 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + mean fill                |  0.0360 | nan      |        nan      | False            |
| block       | 0.2000 | MiniRocket + zero fill                |  0.0167 | nan      |        nan      | False            |
| block       | 0.2000 | MultiRocket + linear interp.          | -0.0204 | nan      |        nan      | False            |
| block       | 0.2000 | Native masked MiniRocket (group-mean) |  0.0089 | nan      |        nan      | False            |
| block       | 0.2000 | w/o weighting (γ=0)                   |  0.0038 | nan      |        nan      | False            |
| block       | 0.5000 | 1-NN ED + linear interp.              |  0.1265 | nan      |        nan      | False            |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    | -0.0069 | nan      |        nan      | False            |
| block       | 0.5000 | LightGBM (native NaN)                 |  0.0682 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + LOCF                     |  0.0187 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + kNN impute               | -0.0430 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + linear interp.           |  0.0063 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + mean fill                |  0.0756 | nan      |        nan      | False            |
| block       | 0.5000 | MiniRocket + zero fill                |  0.0592 | nan      |        nan      | False            |
| block       | 0.5000 | MultiRocket + linear interp.          | -0.0023 | nan      |        nan      | False            |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |  0.0252 | nan      |        nan      | False            |
| block       | 0.5000 | w/o weighting (γ=0)                   |  0.0113 | nan      |        nan      | False            |
| block       | 0.8000 | 1-NN ED + linear interp.              |  0.0751 | nan      |        nan      | False            |
| block       | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0131 | nan      |        nan      | False            |
| block       | 0.8000 | LightGBM (native NaN)                 |  0.0623 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + LOCF                     |  0.0366 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + kNN impute               |  0.0019 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + linear interp.           |  0.0179 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + mean fill                |  0.0693 | nan      |        nan      | False            |
| block       | 0.8000 | MiniRocket + zero fill                |  0.0277 | nan      |        nan      | False            |
| block       | 0.8000 | MultiRocket + linear interp.          |  0.0095 | nan      |        nan      | False            |
| block       | 0.8000 | Native masked MiniRocket (group-mean) |  0.0188 | nan      |        nan      | False            |
| block       | 0.8000 | w/o weighting (γ=0)                   |  0.0180 | nan      |        nan      | False            |
| mcar        | 0.2000 | 1-NN ED + linear interp.              |  0.1308 |   0.1365 |          0.0040 | True             |
| mcar        | 0.2000 | Hydra-MultiRocket + linear interp.    | -0.0147 |  -0.0101 |          0.0033 | True             |
| mcar        | 0.2000 | LightGBM (native NaN)                 |  0.0777 |   0.0667 |          0.0077 | True             |
| mcar        | 0.2000 | MiniRocket + LOCF                     |  0.0010 |   0.0104 |          0.0066 | True             |
| mcar        | 0.2000 | MiniRocket + kNN impute               | -0.0260 |  -0.0157 |          0.0073 | True             |
| mcar        | 0.2000 | MiniRocket + linear interp.           | -0.0026 |   0.0055 |          0.0057 | False            |
| mcar        | 0.2000 | MiniRocket + mean fill                |  0.0447 |   0.0279 |          0.0119 | True             |
| mcar        | 0.2000 | MiniRocket + zero fill                |  0.0314 |   0.0177 |          0.0096 | True             |
| mcar        | 0.2000 | MultiRocket + linear interp.          | -0.0152 |  -0.0192 |          0.0028 | True             |
| mcar        | 0.2000 | Native masked MiniRocket (group-mean) |  0.0028 |   0.0113 |          0.0060 | True             |
| mcar        | 0.2000 | w/o weighting (γ=0)                   |  0.0028 |   0.0007 |          0.0015 | True             |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |  0.1230 | nan      |        nan      | False            |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |  0.0058 | nan      |        nan      | False            |
| mcar        | 0.5000 | LightGBM (native NaN)                 |  0.1303 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + LOCF                     |  0.0079 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + kNN impute               |  0.0178 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + linear interp.           |  0.0030 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + mean fill                |  0.0621 | nan      |        nan      | False            |
| mcar        | 0.5000 | MiniRocket + zero fill                |  0.0540 | nan      |        nan      | False            |
| mcar        | 0.5000 | MultiRocket + linear interp.          |  0.0025 | nan      |        nan      | False            |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |  0.0307 | nan      |        nan      | False            |
| mcar        | 0.5000 | w/o weighting (γ=0)                   |  0.0029 | nan      |        nan      | False            |
| mcar        | 0.8000 | 1-NN ED + linear interp.              |  0.1338 | nan      |        nan      | False            |
| mcar        | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0063 | nan      |        nan      | False            |
| mcar        | 0.8000 | LightGBM (native NaN)                 |  0.2268 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + LOCF                     |  0.0169 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + kNN impute               |  0.0685 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + linear interp.           | -0.0098 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + mean fill                |  0.1364 | nan      |        nan      | False            |
| mcar        | 0.8000 | MiniRocket + zero fill                |  0.1196 | nan      |        nan      | False            |
| mcar        | 0.8000 | MultiRocket + linear interp.          |  0.0086 | nan      |        nan      | False            |
| mcar        | 0.8000 | Native masked MiniRocket (group-mean) |  0.0663 | nan      |        nan      | False            |
| mcar        | 0.8000 | w/o weighting (γ=0)                   | -0.0087 | nan      |        nan      | False            |
| mnar        | 0.2000 | 1-NN ED + linear interp.              |  0.1549 | nan      |        nan      | False            |
| mnar        | 0.2000 | Hydra-MultiRocket + linear interp.    | -0.0009 | nan      |        nan      | False            |
| mnar        | 0.2000 | LightGBM (native NaN)                 |  0.0612 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + LOCF                     |  0.0093 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + kNN impute               |  0.0045 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + linear interp.           |  0.0048 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + mean fill                |  0.0446 | nan      |        nan      | False            |
| mnar        | 0.2000 | MiniRocket + zero fill                |  0.0389 | nan      |        nan      | False            |
| mnar        | 0.2000 | MultiRocket + linear interp.          | -0.0010 | nan      |        nan      | False            |
| mnar        | 0.2000 | Native masked MiniRocket (group-mean) |  0.0100 | nan      |        nan      | False            |
| mnar        | 0.2000 | w/o weighting (γ=0)                   | -0.0023 | nan      |        nan      | False            |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |  0.1542 | nan      |        nan      | False            |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |  0.0060 | nan      |        nan      | False            |
| mnar        | 0.5000 | LightGBM (native NaN)                 |  0.0944 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + LOCF                     |  0.0155 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + kNN impute               |  0.0646 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + linear interp.           |  0.0333 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + mean fill                |  0.1024 | nan      |        nan      | False            |
| mnar        | 0.5000 | MiniRocket + zero fill                |  0.0754 | nan      |        nan      | False            |
| mnar        | 0.5000 | MultiRocket + linear interp.          |  0.0099 | nan      |        nan      | False            |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |  0.0032 | nan      |        nan      | False            |
| mnar        | 0.5000 | w/o weighting (γ=0)                   |  0.0292 | nan      |        nan      | False            |
| mnar        | 0.8000 | 1-NN ED + linear interp.              |  0.1422 | nan      |        nan      | False            |
| mnar        | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0183 | nan      |        nan      | False            |
| mnar        | 0.8000 | LightGBM (native NaN)                 |  0.1033 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + LOCF                     |  0.0407 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + kNN impute               |  0.0405 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + linear interp.           |  0.0324 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + mean fill                |  0.0683 | nan      |        nan      | False            |
| mnar        | 0.8000 | MiniRocket + zero fill                |  0.0522 | nan      |        nan      | False            |
| mnar        | 0.8000 | MultiRocket + linear interp.          |  0.0224 | nan      |        nan      | False            |
| mnar        | 0.8000 | Native masked MiniRocket (group-mean) | -0.0040 | nan      |        nan      | False            |
| mnar        | 0.8000 | w/o weighting (γ=0)                   |  0.0278 | nan      |        nan      | False            |