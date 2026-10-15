import pandas as pd


def mark_to_market(position, close: float, cfg: dict) -> float:
    direction = 1 if position["signal"].side == "long" else -1
    point_value = float(cfg.get("costs", {}).get("point_value_per_lot", 1.0))
    return (close - position["entry"]) * direction * point_value * position["lots"]


def equity_curve(index, balances, unrealized) -> pd.Series:
    return pd.Series([b + u for b, u in zip(balances, unrealized)], index=index, dtype=float)
