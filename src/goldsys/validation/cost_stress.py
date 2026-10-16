from copy import deepcopy


def cost_stress(cfg: dict, run, multipliers=(0.5, 1.0, 1.5, 2.0)):
    rows = []
    for multiplier in multipliers:
        stressed = deepcopy(cfg)
        costs = stressed.setdefault("costs", {})
        costs["spread_points"] = float(costs.get("spread_points", 0.0)) * multiplier
        costs["slippage_points"] = float(costs.get("slippage_points", 0.0)) * multiplier
        metrics = run(stressed)
        rows.append({"cost_multiplier": multiplier, **metrics})
    return rows
