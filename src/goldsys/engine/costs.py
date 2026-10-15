import math
import pandas as pd


def _spread(cfg: dict, timestamp=None) -> float:
    costs = cfg.get("costs", {})
    spread = float(costs.get("spread_points", 0.0))
    if costs.get("rollover_hour") is not None and getattr(timestamp, "hour", None) == int(costs["rollover_hour"]):
        spread *= float(costs.get("rollover_spread_multiplier", 1.0))
    return spread


def entry_fill(raw_price: float, side: str, cfg: dict, timestamp=None) -> float:
    half = _spread(cfg, timestamp) / 2
    slip = float(cfg.get("costs", {}).get("slippage_points", 0.0))
    return float(raw_price) + (half + slip) * (1 if side == "long" else -1)


def exit_fill(raw_price: float, side: str, cfg: dict, timestamp=None) -> float:
    half = _spread(cfg, timestamp) / 2
    slip = float(cfg.get("costs", {}).get("slippage_points", 0.0))
    return float(raw_price) - (half + slip) * (1 if side == "long" else -1)


def swap_cost(lots: float, side: str, cfg: dict, entry_time, exit_time) -> float:
    if entry_time is None or exit_time is None:
        return 0.0
    days = max(0, math.ceil((pd.Timestamp(exit_time) - pd.Timestamp(entry_time)).total_seconds() / 86400))
    key = "swap_long_per_lot_per_day" if side == "long" else "swap_short_per_lot_per_day"
    return days * lots * float(cfg.get("costs", {}).get(key, 0.0))


def round_trip_cost(lots: float, side: str, cfg: dict, entry_time=None, exit_time=None) -> float:
    costs = cfg.get("costs", {})
    spread = _spread(cfg, entry_time) * float(costs.get("point_value_per_lot", 1.0)) * lots
    commission = 2 * float(costs.get("commission_per_lot", 0.0)) * lots
    return spread + commission + swap_cost(lots, side, cfg, entry_time, exit_time)
