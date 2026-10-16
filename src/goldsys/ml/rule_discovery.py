import numpy as np

from .dataset import purged_folds


def _auc(y, score):
    positives = score[np.asarray(y) == 1]
    negatives = score[np.asarray(y) == 0]
    if not len(positives) or not len(negatives):
        return 0.5
    return float((positives[:, None] > negatives[None, :]).mean() + .5 * (positives[:, None] == negatives[None, :]).mean())


def discover_rules(data, max_depth=2, n_splits=5, embargo=1, min_auc=0.55, max_instability=0.15):
    numeric = [c for c in data.columns if c not in {"label", "r_multiple", "signal_time"} and data[c].dtype.kind in "fiu"]
    y = data.label.to_numpy(dtype=int)
    candidates = []
    for feature in numeric:
        values = data[feature].to_numpy(dtype=float)
        for q in np.linspace(.2, .8, max(2, 2 ** max_depth)):
            for operator in [">=", "<="]:
                fold_scores = []
                fold_thresholds = []
                for train, test in purged_folds(data, n_splits, embargo):
                    threshold = float(np.nanquantile(values[train], q))
                    fold_thresholds.append(threshold)
                    score = np.where(values[test] >= threshold if operator == ">=" else values[test] <= threshold, 1.0, 0.0)
                    fold_scores.append(_auc(y[test], score))
                candidates.append({"feature": feature, "operator": operator, "value": float(np.median(fold_thresholds)),
                                   "cv_auc": float(np.mean(fold_scores)), "cv_std": float(np.std(fold_scores)),
                                   "fold_auc": fold_scores})
    candidates.sort(key=lambda row: row["cv_auc"], reverse=True)
    accepted = [row for row in candidates if row["cv_auc"] >= min_auc and row["cv_std"] <= max_instability][:max_depth]
    return {"accepted": bool(accepted), "rules": accepted, "best_auc": candidates[0]["cv_auc"] if candidates else 0.5,
            "candidates": candidates}
