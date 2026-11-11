"""Statistical comparison of classifiers over multiple datasets.

Unit of analysis: dataset. For each (dataset, condition) the metric is first averaged over seeds;
seeds are not treated as independent samples. Tests:
  * Wilcoxon signed-rank test (two-sided, zero differences handled with the 'zsplit' method)
    for paired per-dataset differences (Demsar 2006; Benavoli et al. 2016);
  * Holm step-down correction over the family of comparisons of the proposed method against all others
    within a condition;
  * effect sizes: mean and median paired difference, matched-pairs rank-biserial correlation,
    win/tie/loss counts, and a percentile bootstrap 95% CI of the mean difference (10,000 resamples of datasets).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    m = len(p)
    for k, i in enumerate(order):
        running = max(running, min(1.0, (m - k) * p[i]))
        adj[i] = running
    return adj


def rank_biserial(d):
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    r = pd.Series(np.abs(d)).rank().values
    return float((r[d > 0].sum() - r[d < 0].sum()) / r.sum())


def bootstrap_ci(d, n=10000, seed=0, alpha=0.05):
    rng = np.random.RandomState(seed)
    idx = rng.randint(0, len(d), size=(n, len(d)))
    means = d[idx].mean(1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def compare(table: pd.DataFrame, proposed: str, others, tol=1e-9):
    """table: rows = datasets, columns = methods (seed-averaged metric). Returns one row per comparison."""
    rows = []
    for o in others:
        sub = table[[proposed, o]].dropna()
        d = (sub[proposed] - sub[o]).values
        if np.all(np.abs(d) < tol):
            p = 1.0
        else:
            p = float(wilcoxon(d, zero_method="zsplit", alternative="two-sided").pvalue)
        lo, hi = bootstrap_ci(d)
        rows.append(dict(proposed=proposed, baseline=o, n_datasets=len(d), mean_diff=float(d.mean()),
                         median_diff=float(np.median(d)), ci95_low=lo, ci95_high=hi,
                         wins=int((d > tol).sum()), ties=int((np.abs(d) <= tol).sum()), losses=int((d < -tol).sum()),
                         rank_biserial=rank_biserial(d), p_value=p))
    res = pd.DataFrame(rows)
    if len(res):
        res["p_holm"] = holm(res.p_value.values)
    return res


def mean_ranks(table: pd.DataFrame):
    return table.rank(axis=1, ascending=False).mean().sort_values()
