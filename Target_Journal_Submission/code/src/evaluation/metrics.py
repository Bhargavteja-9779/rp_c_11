"""Classification metrics computed from predictions and decision scores."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score, average_precision_score


def _softmax(s):
    s = s - s.max(1, keepdims=True)
    e = np.exp(s)
    return e / e.sum(1, keepdims=True)


def compute_metrics(y_true, pred, score, classes=None):
    y_true = np.asarray(y_true)
    out = dict(accuracy=accuracy_score(y_true, pred), balanced_accuracy=balanced_accuracy_score(y_true, pred),
               macro_f1=f1_score(y_true, pred, average="macro"))
    try:
        classes = np.arange(score.shape[1]) if classes is None else np.asarray(classes)
        if score.shape[1] == 2:
            out["auroc"] = roc_auc_score(y_true == classes[1], score[:, 1] - score[:, 0])
            out["auprc"] = average_precision_score(y_true == classes[1], score[:, 1] - score[:, 0])
        else:
            mask = np.isin(y_true, classes)
            p = _softmax(score[mask])
            present = np.isin(classes, y_true[mask])
            out["auroc"] = roc_auc_score(y_true[mask], p[:, present] / p[:, present].sum(1, keepdims=True),
                                         multi_class="ovr", average="macro", labels=classes[present])
            out["auprc"] = np.nan
    except Exception:
        out["auroc"] = np.nan
        out["auprc"] = np.nan
    return out
