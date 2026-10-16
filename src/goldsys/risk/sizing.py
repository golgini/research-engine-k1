import math


def fixed_fractional_lots(equity, stop_distance, cfg):
    risk = cfg.get("risk", {})
    target = float(equity) * float(risk.get("risk_per_trade_pct", 0.5)) / 100
    point_value = float(cfg.get("costs", {}).get("point_value_per_lot", 1.0))
    distance = float(stop_distance)
    if distance <= 0 or point_value <= 0:
        return 0.0
    raw = target / (distance * point_value)
    step = float(risk.get("lot_step", 0.01))
    minimum = float(risk.get("min_lot", 0.01))
    maximum = float(risk.get("max_lot", 5.0))
    if raw < minimum and minimum * distance * point_value > 2 * target:
        return 0.0
    return min(maximum, max(minimum, math.floor(raw / step) * step))
