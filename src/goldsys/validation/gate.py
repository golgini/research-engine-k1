def evaluate_gate(metrics: dict, cfg: dict | None = None) -> dict:
    gate = (cfg or {}).get("validation", {}).get("gate", {})
    profit_factor = metrics.get("profit_factor")
    if profit_factor is None:
        profit_factor = float("inf") if metrics.get("net_profit", 0) > 0 else 0.0
    checks = {
        "minimum_trades": int(metrics.get("trades", 0)) >= int(gate.get("min_trades", 20)),
        "profit_factor": profit_factor >= float(gate.get("min_profit_factor", 1.25)),
        "maximum_drawdown": metrics.get("max_drawdown_pct", float("inf")) <= float(gate.get("max_drawdown_pct", 25)),
    }
    return {"checks": checks, "passed": all(checks.values()), "metrics": metrics}
