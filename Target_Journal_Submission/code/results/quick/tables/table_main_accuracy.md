| mechanism   |   rate | method                                |   mean_accuracy |   std_accuracy |   mean_balanced_accuracy |   mean_macro_f1 |
|:------------|-------:|:--------------------------------------|----------------:|---------------:|-------------------------:|----------------:|
| block       | 0.5000 | MissRocket (proposed)                 |          0.7702 |         0.1327 |                   0.7619 |          0.7634 |
| block       | 0.5000 | MiniRocket + linear interp.           |          0.7217 |         0.1153 |                   0.7071 |          0.7113 |
| block       | 0.5000 | MiniRocket + zero fill                |          0.5954 |         0.1570 |                   0.5811 |          0.5842 |
| block       | 0.5000 | MiniRocket + mean fill                |          0.5686 |         0.1394 |                   0.5499 |          0.5513 |
| block       | 0.5000 | MiniRocket + LOCF                     |          0.6668 |         0.1816 |                   0.6518 |          0.6551 |
| block       | 0.5000 | MiniRocket + kNN impute               |          0.8032 |         0.1019 |                   0.7939 |          0.7947 |
| block       | 0.5000 | MultiRocket + linear interp.          |          0.7711 |         0.1136 |                   0.7624 |          0.7642 |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.7805 |         0.1119 |                   0.7730 |          0.7742 |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |          0.6427 |         0.2006 |                   0.6324 |          0.6322 |
| block       | 0.5000 | LightGBM (native NaN)                 |          0.6708 |         0.1603 |                   0.6553 |          0.6597 |
| block       | 0.5000 | 1-NN ED + linear interp.              |          0.6468 |         0.1865 |                   0.6392 |          0.6394 |
| block       | 0.5000 | w/o weighting (γ=0)                   |          0.7417 |         0.0984 |                   0.7295 |          0.7324 |
| mcar        | 0.5000 | MissRocket (proposed)                 |          0.8806 |         0.0977 |                   0.8744 |          0.8732 |
| mcar        | 0.5000 | MiniRocket + linear interp.           |          0.8894 |         0.0849 |                   0.8862 |          0.8837 |
| mcar        | 0.5000 | MiniRocket + zero fill                |          0.7597 |         0.1053 |                   0.7459 |          0.7488 |
| mcar        | 0.5000 | MiniRocket + mean fill                |          0.7492 |         0.1030 |                   0.7359 |          0.7384 |
| mcar        | 0.5000 | MiniRocket + LOCF                     |          0.8884 |         0.0858 |                   0.8850 |          0.8836 |
| mcar        | 0.5000 | MiniRocket + kNN impute               |          0.8894 |         0.0776 |                   0.8907 |          0.8868 |
| mcar        | 0.5000 | MultiRocket + linear interp.          |          0.9040 |         0.0779 |                   0.8971 |          0.8984 |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.8983 |         0.0823 |                   0.8918 |          0.8926 |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |          0.7994 |         0.1713 |                   0.7937 |          0.7939 |
| mcar        | 0.5000 | LightGBM (native NaN)                 |          0.7194 |         0.0937 |                   0.7067 |          0.7086 |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |          0.8522 |         0.0534 |                   0.8479 |          0.8468 |
| mcar        | 0.5000 | w/o weighting (γ=0)                   |          0.8957 |         0.0913 |                   0.8918 |          0.8901 |
| mnar        | 0.5000 | MissRocket (proposed)                 |          0.8625 |         0.1211 |                   0.8638 |          0.8582 |
| mnar        | 0.5000 | MiniRocket + linear interp.           |          0.8557 |         0.1089 |                   0.8590 |          0.8517 |
| mnar        | 0.5000 | MiniRocket + zero fill                |          0.8149 |         0.1610 |                   0.8108 |          0.8097 |
| mnar        | 0.5000 | MiniRocket + mean fill                |          0.8130 |         0.1832 |                   0.8130 |          0.8100 |
| mnar        | 0.5000 | MiniRocket + LOCF                     |          0.8383 |         0.1234 |                   0.8363 |          0.8324 |
| mnar        | 0.5000 | MiniRocket + kNN impute               |          0.8402 |         0.1209 |                   0.8380 |          0.8325 |
| mnar        | 0.5000 | MultiRocket + linear interp.          |          0.8744 |         0.1040 |                   0.8716 |          0.8697 |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.8778 |         0.1021 |                   0.8747 |          0.8729 |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |          0.7968 |         0.2346 |                   0.8001 |          0.7884 |
| mnar        | 0.5000 | LightGBM (native NaN)                 |          0.7633 |         0.1457 |                   0.7582 |          0.7572 |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |          0.7583 |         0.0296 |                   0.7476 |          0.7449 |
| mnar        | 0.5000 | w/o weighting (γ=0)                   |          0.8544 |         0.1229 |                   0.8556 |          0.8497 |