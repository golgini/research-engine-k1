from dataclasses import dataclass

from .costs import entry_fill, exit_fill, round_trip_cost


@dataclass
class Fill:
    signal: object
    time: object
    price: float


def pending_fill(signal, bar, cfg, bars_held: int):
    if signal.expiry_bars is not None and bars_held > signal.expiry_bars:
        return None
    side = signal.side
    raw = signal.entry_price
    if signal.entry_type == "market_next_open":
        raw = float(bar.open)
    elif signal.entry_type == "stop":
        if raw is None or (bar.high < raw if side == "long" else bar.low > raw):
            return None
        raw = float(bar.open) if (bar.open >= raw if side == "long" else bar.open <= raw) else float(raw)
    elif signal.entry_type == "limit":
        if raw is None or (bar.low > raw if side == "long" else bar.high < raw):
            return None
        raw = float(bar.open) if (bar.open <= raw if side == "long" else bar.open >= raw) else float(raw)
    else:
        raise ValueError(f"Unknown entry type: {signal.entry_type}")
    return Fill(signal, bar.name, entry_fill(raw, side, cfg, bar.name))


def protective_exit(position, bar, cfg):
    signal = position["signal"]
    long = signal.side == "long"
    hit_sl = bar.low <= signal.stop_loss if long else bar.high >= signal.stop_loss
    hit_tp = signal.take_profit is not None and (bar.high >= signal.take_profit if long else bar.low <= signal.take_profit)
    if not hit_sl and not hit_tp:
        return None
    conflict = cfg.get("engine", {}).get("intrabar_conflict", "sl_first")
    if hit_sl and hit_tp:
        reason = "tp" if conflict == "tp_first" else "sl"
        if reason == "sl" and ((long and bar.open <= signal.stop_loss) or (not long and bar.open >= signal.stop_loss)):
            return reason, float(bar.open)
        return reason, signal.take_profit if reason == "tp" else signal.stop_loss
    if hit_sl:
        raw = float(bar.open) if (long and bar.open <= signal.stop_loss) or (not long and bar.open >= signal.stop_loss) else signal.stop_loss
        return "sl", raw
    return "tp", signal.take_profit


def close_position(position, bar, reason, raw_price, cfg):
    side = position["signal"].side
    price = exit_fill(raw_price, side, cfg, bar.name)
    direction = 1 if side == "long" else -1
    point_value = float(cfg.get("costs", {}).get("point_value_per_lot", 1.0))
    gross = (price - position["entry"]) * direction * point_value * position["lots"]
    costs = round_trip_cost(position["lots"], side, cfg, position["entry_time"], bar.name)
    return price, gross, costs, gross - costs
