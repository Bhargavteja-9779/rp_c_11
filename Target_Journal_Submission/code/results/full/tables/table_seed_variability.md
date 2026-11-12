| mechanism   |   rate | baseline                              |       0 |       1 |       2 |   sd_over_seeds | sign_agreement   |
|:------------|-------:|:--------------------------------------|--------:|--------:|--------:|----------------:|:-----------------|
| block       | 0.2000 | 1-NN ED + linear interp.              |  0.1907 |  0.1980 |  0.1910 |          0.0041 | True             |
| block       | 0.2000 | Hydra-MultiRocket + linear interp.    |  0.0066 |  0.0101 |  0.0218 |          0.0079 | True             |
| block       | 0.2000 | LightGBM (native NaN)                 |  0.1346 |  0.1298 |  0.1356 |          0.0031 | True             |
| block       | 0.2000 | MiniRocket + LOCF                     |  0.0173 |  0.0207 |  0.0361 |          0.0100 | True             |
| block       | 0.2000 | MiniRocket + kNN impute               | -0.0219 | -0.0218 | -0.0208 |          0.0006 | True             |
| block       | 0.2000 | MiniRocket + linear interp.           |  0.0169 |  0.0208 |  0.0151 |          0.0029 | True             |
| block       | 0.2000 | MiniRocket + mean fill                |  0.0402 |  0.0428 |  0.0630 |          0.0125 | True             |
| block       | 0.2000 | MiniRocket + zero fill                |  0.0331 |  0.0436 |  0.0529 |          0.0099 | True             |
| block       | 0.2000 | MultiRocket + linear interp.          |  0.0038 |  0.0143 |  0.0220 |          0.0091 | True             |
| block       | 0.2000 | Native masked MiniRocket (group-mean) |  0.0338 |  0.0320 |  0.0369 |          0.0025 | True             |
| block       | 0.2000 | w/o weighting (γ=0)                   |  0.0144 |  0.0152 |  0.0131 |          0.0011 | True             |
| block       | 0.5000 | 1-NN ED + linear interp.              |  0.1770 |  0.1882 |  0.1845 |          0.0057 | True             |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    |  0.0228 |  0.0313 |  0.0281 |          0.0043 | True             |
| block       | 0.5000 | LightGBM (native NaN)                 |  0.1046 |  0.1200 |  0.1077 |          0.0081 | True             |
| block       | 0.5000 | MiniRocket + LOCF                     |  0.0544 |  0.0517 |  0.0564 |          0.0024 | True             |
| block       | 0.5000 | MiniRocket + kNN impute               | -0.0350 | -0.0169 | -0.0275 |          0.0091 | True             |
| block       | 0.5000 | MiniRocket + linear interp.           |  0.0419 |  0.0416 |  0.0418 |          0.0002 | True             |
| block       | 0.5000 | MiniRocket + mean fill                |  0.0903 |  0.1028 |  0.1027 |          0.0072 | True             |
| block       | 0.5000 | MiniRocket + zero fill                |  0.0681 |  0.0788 |  0.0771 |          0.0058 | True             |
| block       | 0.5000 | MultiRocket + linear interp.          |  0.0270 |  0.0279 |  0.0296 |          0.0013 | True             |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |  0.0389 |  0.0414 |  0.0496 |          0.0056 | True             |
| block       | 0.5000 | w/o weighting (γ=0)                   |  0.0341 |  0.0375 |  0.0277 |          0.0050 | True             |
| block       | 0.8000 | 1-NN ED + linear interp.              |  0.1327 |  0.1377 |  0.1466 |          0.0070 | True             |
| block       | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0269 |  0.0310 |  0.0348 |          0.0040 | True             |
| block       | 0.8000 | LightGBM (native NaN)                 |  0.0678 |  0.0636 |  0.0780 |          0.0074 | True             |
| block       | 0.8000 | MiniRocket + LOCF                     |  0.0576 |  0.0688 |  0.0669 |          0.0060 | True             |
| block       | 0.8000 | MiniRocket + kNN impute               | -0.0033 | -0.0021 |  0.0128 |          0.0090 | False            |
| block       | 0.8000 | MiniRocket + linear interp.           |  0.0529 |  0.0518 |  0.0520 |          0.0006 | True             |
| block       | 0.8000 | MiniRocket + mean fill                |  0.0998 |  0.0973 |  0.1110 |          0.0073 | True             |
| block       | 0.8000 | MiniRocket + zero fill                |  0.0664 |  0.0638 |  0.0861 |          0.0122 | True             |
| block       | 0.8000 | MultiRocket + linear interp.          |  0.0314 |  0.0329 |  0.0368 |          0.0028 | True             |
| block       | 0.8000 | Native masked MiniRocket (group-mean) |  0.0335 |  0.0344 |  0.0343 |          0.0005 | True             |
| block       | 0.8000 | w/o weighting (γ=0)                   |  0.0361 |  0.0387 |  0.0330 |          0.0028 | True             |
| mcar        | 0.2000 | 1-NN ED + linear interp.              |  0.1727 |  0.1619 |  0.1696 |          0.0056 | True             |
| mcar        | 0.2000 | Hydra-MultiRocket + linear interp.    | -0.0064 | -0.0126 | -0.0082 |          0.0032 | True             |
| mcar        | 0.2000 | LightGBM (native NaN)                 |  0.1557 |  0.1532 |  0.1534 |          0.0014 | True             |
| mcar        | 0.2000 | MiniRocket + LOCF                     |  0.0045 |  0.0040 |  0.0089 |          0.0027 | True             |
| mcar        | 0.2000 | MiniRocket + kNN impute               |  0.0015 |  0.0028 |  0.0060 |          0.0023 | True             |
| mcar        | 0.2000 | MiniRocket + linear interp.           | -0.0032 | -0.0082 | -0.0025 |          0.0031 | True             |
| mcar        | 0.2000 | MiniRocket + mean fill                |  0.0729 |  0.0714 |  0.0664 |          0.0034 | True             |
| mcar        | 0.2000 | MiniRocket + zero fill                |  0.0789 |  0.0734 |  0.0766 |          0.0028 | True             |
| mcar        | 0.2000 | MultiRocket + linear interp.          | -0.0044 | -0.0112 | -0.0045 |          0.0039 | True             |
| mcar        | 0.2000 | Native masked MiniRocket (group-mean) |  0.0282 |  0.0230 |  0.0357 |          0.0064 | True             |
| mcar        | 0.2000 | w/o weighting (γ=0)                   | -0.0052 | -0.0115 | -0.0047 |          0.0038 | True             |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |  0.1629 |  0.1690 |  0.1568 |          0.0061 | True             |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    | -0.0106 | -0.0059 | -0.0076 |          0.0024 | True             |
| mcar        | 0.5000 | LightGBM (native NaN)                 |  0.1812 |  0.1992 |  0.1913 |          0.0090 | True             |
| mcar        | 0.5000 | MiniRocket + LOCF                     |  0.0109 |  0.0186 |  0.0124 |          0.0040 | True             |
| mcar        | 0.5000 | MiniRocket + kNN impute               |  0.0399 |  0.0361 |  0.0367 |          0.0020 | True             |
| mcar        | 0.5000 | MiniRocket + linear interp.           | -0.0063 | -0.0029 | -0.0048 |          0.0017 | True             |
| mcar        | 0.5000 | MiniRocket + mean fill                |  0.1116 |  0.1236 |  0.1146 |          0.0062 | True             |
| mcar        | 0.5000 | MiniRocket + zero fill                |  0.1150 |  0.1272 |  0.1169 |          0.0065 | True             |
| mcar        | 0.5000 | MultiRocket + linear interp.          | -0.0099 | -0.0070 | -0.0046 |          0.0027 | True             |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |  0.0580 |  0.0638 |  0.0560 |          0.0040 | True             |
| mcar        | 0.5000 | w/o weighting (γ=0)                   | -0.0067 | -0.0075 | -0.0075 |          0.0005 | True             |
| mcar        | 0.8000 | 1-NN ED + linear interp.              |  0.1607 |  0.1560 |  0.1577 |          0.0024 | True             |
| mcar        | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0144 |  0.0033 |  0.0124 |          0.0059 | True             |
| mcar        | 0.8000 | LightGBM (native NaN)                 |  0.2344 |  0.2339 |  0.2358 |          0.0010 | True             |
| mcar        | 0.8000 | MiniRocket + LOCF                     |  0.0310 |  0.0363 |  0.0386 |          0.0039 | True             |
| mcar        | 0.8000 | MiniRocket + kNN impute               |  0.0714 |  0.0678 |  0.0833 |          0.0081 | True             |
| mcar        | 0.8000 | MiniRocket + linear interp.           |  0.0055 | -0.0030 |  0.0046 |          0.0046 | False            |
| mcar        | 0.8000 | MiniRocket + mean fill                |  0.1817 |  0.1894 |  0.1931 |          0.0058 | True             |
| mcar        | 0.8000 | MiniRocket + zero fill                |  0.1702 |  0.1679 |  0.1692 |          0.0011 | True             |
| mcar        | 0.8000 | MultiRocket + linear interp.          |  0.0127 | -0.0007 |  0.0049 |          0.0067 | False            |
| mcar        | 0.8000 | Native masked MiniRocket (group-mean) |  0.1027 |  0.1017 |  0.1042 |          0.0012 | True             |
| mcar        | 0.8000 | w/o weighting (γ=0)                   |  0.0025 | -0.0014 |  0.0045 |          0.0030 | False            |
| mnar        | 0.2000 | 1-NN ED + linear interp.              |  0.1847 |  0.1821 |  0.1842 |          0.0014 | True             |
| mnar        | 0.2000 | Hydra-MultiRocket + linear interp.    |  0.0058 |  0.0049 |  0.0088 |          0.0020 | True             |
| mnar        | 0.2000 | LightGBM (native NaN)                 |  0.1531 |  0.1440 |  0.1461 |          0.0048 | True             |
| mnar        | 0.2000 | MiniRocket + LOCF                     |  0.0138 |  0.0026 |  0.0155 |          0.0070 | True             |
| mnar        | 0.2000 | MiniRocket + kNN impute               |  0.0127 |  0.0082 |  0.0115 |          0.0023 | True             |
| mnar        | 0.2000 | MiniRocket + linear interp.           |  0.0079 |  0.0012 |  0.0064 |          0.0035 | True             |
| mnar        | 0.2000 | MiniRocket + mean fill                |  0.0536 |  0.0560 |  0.0531 |          0.0016 | True             |
| mnar        | 0.2000 | MiniRocket + zero fill                |  0.0476 |  0.0467 |  0.0409 |          0.0036 | True             |
| mnar        | 0.2000 | MultiRocket + linear interp.          |  0.0072 | -0.0014 |  0.0104 |          0.0061 | False            |
| mnar        | 0.2000 | Native masked MiniRocket (group-mean) |  0.0225 |  0.0237 |  0.0123 |          0.0062 | True             |
| mnar        | 0.2000 | w/o weighting (γ=0)                   |  0.0033 |  0.0004 |  0.0047 |          0.0022 | True             |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |  0.1849 |  0.1926 |  0.1985 |          0.0068 | True             |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |  0.0057 |  0.0100 |  0.0093 |          0.0023 | True             |
| mnar        | 0.5000 | LightGBM (native NaN)                 |  0.1513 |  0.1500 |  0.1545 |          0.0023 | True             |
| mnar        | 0.5000 | MiniRocket + LOCF                     |  0.0219 |  0.0193 |  0.0237 |          0.0022 | True             |
| mnar        | 0.5000 | MiniRocket + kNN impute               |  0.0558 |  0.0522 |  0.0591 |          0.0035 | True             |
| mnar        | 0.5000 | MiniRocket + linear interp.           |  0.0183 |  0.0140 |  0.0183 |          0.0024 | True             |
| mnar        | 0.5000 | MiniRocket + mean fill                |  0.1027 |  0.0960 |  0.1068 |          0.0055 | True             |
| mnar        | 0.5000 | MiniRocket + zero fill                |  0.0795 |  0.0743 |  0.0895 |          0.0077 | True             |
| mnar        | 0.5000 | MultiRocket + linear interp.          |  0.0079 |  0.0089 |  0.0092 |          0.0007 | True             |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |  0.0410 |  0.0285 |  0.0419 |          0.0075 | True             |
| mnar        | 0.5000 | w/o weighting (γ=0)                   |  0.0172 |  0.0140 |  0.0166 |          0.0017 | True             |
| mnar        | 0.8000 | 1-NN ED + linear interp.              |  0.1759 |  0.1836 |  0.1847 |          0.0048 | True             |
| mnar        | 0.8000 | Hydra-MultiRocket + linear interp.    |  0.0310 |  0.0432 |  0.0366 |          0.0061 | True             |
| mnar        | 0.8000 | LightGBM (native NaN)                 |  0.1526 |  0.1572 |  0.1562 |          0.0024 | True             |
| mnar        | 0.8000 | MiniRocket + LOCF                     |  0.0467 |  0.0486 |  0.0462 |          0.0013 | True             |
| mnar        | 0.8000 | MiniRocket + kNN impute               |  0.0765 |  0.0824 |  0.0711 |          0.0057 | True             |
| mnar        | 0.8000 | MiniRocket + linear interp.           |  0.0346 |  0.0463 |  0.0405 |          0.0058 | True             |
| mnar        | 0.8000 | MiniRocket + mean fill                |  0.1115 |  0.1130 |  0.1161 |          0.0024 | True             |
| mnar        | 0.8000 | MiniRocket + zero fill                |  0.0903 |  0.1026 |  0.0842 |          0.0094 | True             |
| mnar        | 0.8000 | MultiRocket + linear interp.          |  0.0273 |  0.0415 |  0.0317 |          0.0073 | True             |
| mnar        | 0.8000 | Native masked MiniRocket (group-mean) |  0.0356 |  0.0504 |  0.0430 |          0.0074 | True             |
| mnar        | 0.8000 | w/o weighting (γ=0)                   |  0.0278 |  0.0391 |  0.0349 |          0.0057 | True             |