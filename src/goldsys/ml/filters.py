import pandas as pd


def apply_rule_filter(features: pd.DataFrame, rules: list[dict]) -> pd.Series:
    mask = pd.Series(True, index=features.index)
    for rule in rules:
        if rule["operator"] == ">=":
            mask &= features[rule["feature"]] >= rule["value"]
        elif rule["operator"] == "<=":
            mask &= features[rule["feature"]] <= rule["value"]
        else:
            raise ValueError(f"Unsupported rule operator: {rule['operator']}")
    return mask


def rules_markdown(result: dict) -> str:
    lines = ["# Discovered rules", "", f"Accepted: **{result['accepted']}**", f"Best cross-validated AUC: {result['best_auc']:.3f}", ""]
    if not result["rules"]:
        return "\n".join(lines + ["No rule passed the AUC and stability gates."])
    lines += ["| Feature | Rule | Threshold | CV AUC | CV std |", "|---|---|---:|---:|---:|"]
    lines += [f"| {r['feature']} | {r['operator']} | {r['value']:.6g} | {r['cv_auc']:.3f} | {r['cv_std']:.3f} |" for r in result["rules"]]
    return "\n".join(lines)
