| mechanism   |   rate | method                                |   mean_accuracy |   std_accuracy |   mean_balanced_accuracy |   mean_macro_f1 |
|:------------|-------:|:--------------------------------------|----------------:|---------------:|-------------------------:|----------------:|
| block       | 0.2000 | MissRocket (proposed)                 |          0.7913 |         0.1599 |                   0.7675 |          0.7641 |
| block       | 0.2000 | MiniRocket + linear interp.           |          0.7806 |         0.1636 |                   0.7576 |          0.7531 |
| block       | 0.2000 | MiniRocket + zero fill                |          0.7467 |         0.1745 |                   0.7218 |          0.7166 |
| block       | 0.2000 | MiniRocket + mean fill                |          0.7435 |         0.1741 |                   0.7183 |          0.7138 |
| block       | 0.2000 | MiniRocket + LOCF                     |          0.7664 |         0.1699 |                   0.7417 |          0.7366 |
| block       | 0.2000 | MiniRocket + kNN impute               |          0.8095 |         0.1544 |                   0.7870 |          0.7841 |
| block       | 0.2000 | MultiRocket + linear interp.          |          0.7925 |         0.1584 |                   0.7691 |          0.7655 |
| block       | 0.2000 | Hydra-MultiRocket + linear interp.    |          0.7942 |         0.1568 |                   0.7714 |          0.7683 |
| block       | 0.2000 | Native masked MiniRocket (group-mean) |          0.7501 |         0.1735 |                   0.7242 |          0.7192 |
| block       | 0.2000 | LightGBM (native NaN)                 |          0.6660 |         0.2143 |                   0.6404 |          0.6341 |
| block       | 0.2000 | 1-NN ED + linear interp.              |          0.6154 |         0.2047 |                   0.5976 |          0.5863 |
| block       | 0.2000 | w/o weighting (γ=0)                   |          0.7847 |         0.1613 |                   0.7612 |          0.7568 |
| block       | 0.5000 | MissRocket (proposed)                 |          0.6914 |         0.1889 |                   0.6642 |          0.6579 |
| block       | 0.5000 | MiniRocket + linear interp.           |          0.6520 |         0.1931 |                   0.6231 |          0.6159 |
| block       | 0.5000 | MiniRocket + zero fill                |          0.6279 |         0.1832 |                   0.5972 |          0.5912 |
| block       | 0.5000 | MiniRocket + mean fill                |          0.6054 |         0.1923 |                   0.5755 |          0.5674 |
| block       | 0.5000 | MiniRocket + LOCF                     |          0.6324 |         0.1910 |                   0.6029 |          0.5946 |
| block       | 0.5000 | MiniRocket + kNN impute               |          0.7216 |         0.1795 |                   0.6965 |          0.6908 |
| block       | 0.5000 | MultiRocket + linear interp.          |          0.6674 |         0.1936 |                   0.6384 |          0.6333 |
| block       | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.6741 |         0.1936 |                   0.6448 |          0.6402 |
| block       | 0.5000 | Native masked MiniRocket (group-mean) |          0.6426 |         0.1865 |                   0.6126 |          0.6058 |
| block       | 0.5000 | LightGBM (native NaN)                 |          0.5926 |         0.2147 |                   0.5615 |          0.5529 |
| block       | 0.5000 | 1-NN ED + linear interp.              |          0.5225 |         0.2105 |                   0.5028 |          0.4932 |
| block       | 0.5000 | w/o weighting (γ=0)                   |          0.6617 |         0.1924 |                   0.6326 |          0.6255 |
| block       | 0.8000 | MissRocket (proposed)                 |          0.5606 |         0.1965 |                   0.5298 |          0.5201 |
| block       | 0.8000 | MiniRocket + linear interp.           |          0.5160 |         0.2065 |                   0.4873 |          0.4780 |
| block       | 0.8000 | MiniRocket + zero fill                |          0.5049 |         0.2024 |                   0.4751 |          0.4679 |
| block       | 0.8000 | MiniRocket + mean fill                |          0.4761 |         0.2042 |                   0.4459 |          0.4358 |
| block       | 0.8000 | MiniRocket + LOCF                     |          0.4985 |         0.2113 |                   0.4667 |          0.4574 |
| block       | 0.8000 | MiniRocket + kNN impute               |          0.5658 |         0.2084 |                   0.5372 |          0.5278 |
| block       | 0.8000 | MultiRocket + linear interp.          |          0.5325 |         0.2061 |                   0.5063 |          0.4981 |
| block       | 0.8000 | Hydra-MultiRocket + linear interp.    |          0.5328 |         0.2050 |                   0.5065 |          0.4980 |
| block       | 0.8000 | Native masked MiniRocket (group-mean) |          0.5253 |         0.1924 |                   0.4945 |          0.4866 |
| block       | 0.8000 | LightGBM (native NaN)                 |          0.5004 |         0.2126 |                   0.4709 |          0.4588 |
| block       | 0.8000 | 1-NN ED + linear interp.              |          0.4291 |         0.2134 |                   0.4108 |          0.4013 |
| block       | 0.8000 | w/o weighting (γ=0)                   |          0.5342 |         0.2003 |                   0.5055 |          0.4961 |
| mcar        | 0.2000 | MissRocket (proposed)                 |          0.8495 |         0.1448 |                   0.8279 |          0.8259 |
| mcar        | 0.2000 | MiniRocket + linear interp.           |          0.8531 |         0.1431 |                   0.8317 |          0.8296 |
| mcar        | 0.2000 | MiniRocket + zero fill                |          0.7728 |         0.1736 |                   0.7465 |          0.7417 |
| mcar        | 0.2000 | MiniRocket + mean fill                |          0.7724 |         0.1766 |                   0.7447 |          0.7402 |
| mcar        | 0.2000 | MiniRocket + LOCF                     |          0.8415 |         0.1465 |                   0.8205 |          0.8184 |
| mcar        | 0.2000 | MiniRocket + kNN impute               |          0.8350 |         0.1525 |                   0.8151 |          0.8118 |
| mcar        | 0.2000 | MultiRocket + linear interp.          |          0.8520 |         0.1413 |                   0.8312 |          0.8288 |
| mcar        | 0.2000 | Hydra-MultiRocket + linear interp.    |          0.8537 |         0.1396 |                   0.8331 |          0.8312 |
| mcar        | 0.2000 | Native masked MiniRocket (group-mean) |          0.8104 |         0.1590 |                   0.7858 |          0.7815 |
| mcar        | 0.2000 | LightGBM (native NaN)                 |          0.6818 |         0.2115 |                   0.6533 |          0.6460 |
| mcar        | 0.2000 | 1-NN ED + linear interp.              |          0.6820 |         0.2053 |                   0.6652 |          0.6582 |
| mcar        | 0.2000 | w/o weighting (γ=0)                   |          0.8533 |         0.1435 |                   0.8321 |          0.8301 |
| mcar        | 0.5000 | MissRocket (proposed)                 |          0.8237 |         0.1516 |                   0.8011 |          0.7979 |
| mcar        | 0.5000 | MiniRocket + linear interp.           |          0.8296 |         0.1478 |                   0.8065 |          0.8034 |
| mcar        | 0.5000 | MiniRocket + zero fill                |          0.6977 |         0.1807 |                   0.6687 |          0.6605 |
| mcar        | 0.5000 | MiniRocket + mean fill                |          0.6908 |         0.1801 |                   0.6600 |          0.6514 |
| mcar        | 0.5000 | MiniRocket + LOCF                     |          0.8056 |         0.1588 |                   0.7820 |          0.7782 |
| mcar        | 0.5000 | MiniRocket + kNN impute               |          0.7783 |         0.1639 |                   0.7551 |          0.7493 |
| mcar        | 0.5000 | MultiRocket + linear interp.          |          0.8270 |         0.1493 |                   0.8047 |          0.8020 |
| mcar        | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.8298 |         0.1472 |                   0.8078 |          0.8052 |
| mcar        | 0.5000 | Native masked MiniRocket (group-mean) |          0.7386 |         0.1688 |                   0.7109 |          0.7029 |
| mcar        | 0.5000 | LightGBM (native NaN)                 |          0.6131 |         0.2031 |                   0.5787 |          0.5673 |
| mcar        | 0.5000 | 1-NN ED + linear interp.              |          0.6587 |         0.2055 |                   0.6406 |          0.6309 |
| mcar        | 0.5000 | w/o weighting (γ=0)                   |          0.8305 |         0.1457 |                   0.8077 |          0.8049 |
| mcar        | 0.8000 | MissRocket (proposed)                 |          0.7445 |         0.1600 |                   0.7206 |          0.7150 |
| mcar        | 0.8000 | MiniRocket + linear interp.           |          0.7414 |         0.1658 |                   0.7160 |          0.7105 |
| mcar        | 0.8000 | MiniRocket + zero fill                |          0.5817 |         0.1842 |                   0.5513 |          0.5425 |
| mcar        | 0.8000 | MiniRocket + mean fill                |          0.5633 |         0.1872 |                   0.5325 |          0.5224 |
| mcar        | 0.8000 | MiniRocket + LOCF                     |          0.7010 |         0.1744 |                   0.6731 |          0.6661 |
| mcar        | 0.8000 | MiniRocket + kNN impute               |          0.6609 |         0.1838 |                   0.6304 |          0.6199 |
| mcar        | 0.8000 | MultiRocket + linear interp.          |          0.7385 |         0.1694 |                   0.7153 |          0.7093 |
| mcar        | 0.8000 | Hydra-MultiRocket + linear interp.    |          0.7369 |         0.1675 |                   0.7137 |          0.7082 |
| mcar        | 0.8000 | Native masked MiniRocket (group-mean) |          0.6262 |         0.1827 |                   0.5952 |          0.5852 |
| mcar        | 0.8000 | LightGBM (native NaN)                 |          0.5006 |         0.1992 |                   0.4638 |          0.4498 |
| mcar        | 0.8000 | 1-NN ED + linear interp.              |          0.5924 |         0.1986 |                   0.5711 |          0.5625 |
| mcar        | 0.8000 | w/o weighting (γ=0)                   |          0.7434 |         0.1627 |                   0.7185 |          0.7139 |
| mnar        | 0.2000 | MissRocket (proposed)                 |          0.8338 |         0.1471 |                   0.8134 |          0.8109 |
| mnar        | 0.2000 | MiniRocket + linear interp.           |          0.8296 |         0.1512 |                   0.8073 |          0.8051 |
| mnar        | 0.2000 | MiniRocket + zero fill                |          0.7829 |         0.1634 |                   0.7583 |          0.7542 |
| mnar        | 0.2000 | MiniRocket + mean fill                |          0.7750 |         0.1665 |                   0.7501 |          0.7453 |
| mnar        | 0.2000 | MiniRocket + LOCF                     |          0.8233 |         0.1521 |                   0.8001 |          0.7976 |
| mnar        | 0.2000 | MiniRocket + kNN impute               |          0.8193 |         0.1505 |                   0.7972 |          0.7942 |
| mnar        | 0.2000 | MultiRocket + linear interp.          |          0.8299 |         0.1521 |                   0.8090 |          0.8068 |
| mnar        | 0.2000 | Hydra-MultiRocket + linear interp.    |          0.8318 |         0.1500 |                   0.8112 |          0.8091 |
| mnar        | 0.2000 | Native masked MiniRocket (group-mean) |          0.8029 |         0.1557 |                   0.7775 |          0.7740 |
| mnar        | 0.2000 | LightGBM (native NaN)                 |          0.6813 |         0.2127 |                   0.6535 |          0.6461 |
| mnar        | 0.2000 | 1-NN ED + linear interp.              |          0.6617 |         0.2044 |                   0.6445 |          0.6365 |
| mnar        | 0.2000 | w/o weighting (γ=0)                   |          0.8301 |         0.1500 |                   0.8073 |          0.8048 |
| mnar        | 0.5000 | MissRocket (proposed)                 |          0.7904 |         0.1574 |                   0.7660 |          0.7613 |
| mnar        | 0.5000 | MiniRocket + linear interp.           |          0.7748 |         0.1690 |                   0.7500 |          0.7444 |
| mnar        | 0.5000 | MiniRocket + zero fill                |          0.7149 |         0.1760 |                   0.6895 |          0.6825 |
| mnar        | 0.5000 | MiniRocket + mean fill                |          0.6989 |         0.1711 |                   0.6709 |          0.6632 |
| mnar        | 0.5000 | MiniRocket + LOCF                     |          0.7627 |         0.1677 |                   0.7369 |          0.7314 |
| mnar        | 0.5000 | MiniRocket + kNN impute               |          0.7473 |         0.1651 |                   0.7236 |          0.7182 |
| mnar        | 0.5000 | MultiRocket + linear interp.          |          0.7800 |         0.1682 |                   0.7563 |          0.7520 |
| mnar        | 0.5000 | Hydra-MultiRocket + linear interp.    |          0.7823 |         0.1644 |                   0.7582 |          0.7538 |
| mnar        | 0.5000 | Native masked MiniRocket (group-mean) |          0.7542 |         0.1589 |                   0.7280 |          0.7211 |
| mnar        | 0.5000 | LightGBM (native NaN)                 |          0.6359 |         0.2072 |                   0.6054 |          0.5963 |
| mnar        | 0.5000 | 1-NN ED + linear interp.              |          0.6063 |         0.1959 |                   0.5856 |          0.5764 |
| mnar        | 0.5000 | w/o weighting (γ=0)                   |          0.7762 |         0.1681 |                   0.7519 |          0.7468 |
| mnar        | 0.8000 | MissRocket (proposed)                 |          0.6982 |         0.1620 |                   0.6720 |          0.6627 |
| mnar        | 0.8000 | MiniRocket + linear interp.           |          0.6651 |         0.1613 |                   0.6375 |          0.6290 |
| mnar        | 0.8000 | MiniRocket + zero fill                |          0.6331 |         0.1727 |                   0.6054 |          0.5961 |
| mnar        | 0.8000 | MiniRocket + mean fill                |          0.6105 |         0.1742 |                   0.5800 |          0.5711 |
| mnar        | 0.8000 | MiniRocket + LOCF                     |          0.6428 |         0.1703 |                   0.6162 |          0.6078 |
| mnar        | 0.8000 | MiniRocket + kNN impute               |          0.6325 |         0.1795 |                   0.6051 |          0.5927 |
| mnar        | 0.8000 | MultiRocket + linear interp.          |          0.6786 |         0.1688 |                   0.6535 |          0.6468 |
| mnar        | 0.8000 | Hydra-MultiRocket + linear interp.    |          0.6751 |         0.1617 |                   0.6494 |          0.6429 |
| mnar        | 0.8000 | Native masked MiniRocket (group-mean) |          0.6648 |         0.1681 |                   0.6355 |          0.6260 |
| mnar        | 0.8000 | LightGBM (native NaN)                 |          0.5509 |         0.1983 |                   0.5214 |          0.5059 |
| mnar        | 0.8000 | 1-NN ED + linear interp.              |          0.5313 |         0.1827 |                   0.5113 |          0.5018 |
| mnar        | 0.8000 | w/o weighting (γ=0)                   |          0.6692 |         0.1604 |                   0.6417 |          0.6329 |