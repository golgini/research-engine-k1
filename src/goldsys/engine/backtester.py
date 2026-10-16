from dataclasses import dataclass

import pandas as pd

from goldsys.strategies.base import Signal
from .broker_sim import close_position, pending_fill, protective_exit
from .portfolio import equity_curve, mark_to_market
from goldsys.risk.engine import RiskEngine


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.Series
    config_snapshot: dict
    strategy: str
    params: dict
    period: tuple[str, str]


TRADE_COLS = [
    "trade_id", "strategy", "side", "signal_time", "entry_time", "entry_price",
    "exit_time", "exit_price", "exit_reason", "lots", "sl_price", "tp_price",
    "risk_amount", "gross_pnl", "costs", "net_pnl", "r_multiple", "mae", "mfe",
    "bars_held", "meta",
]


def run_backtest(bars, signals: list[Signal], cfg, strategy_name="strategy", params=None, period=("", "")):
    initial = float(cfg.get("engine", {}).get("initial_equity", 10000))
    allow_multiple = bool(cfg.get("engine", {}).get("allow_multiple_positions", False))
    by_time = {s.time: s for s in signals}
    pending, active = [], []
    rows, balances, unrealized = [], [], []
    balance = initial
    risk_engine = RiskEngine(cfg) if "risk" in cfg else None

    for i, (timestamp, bar) in enumerate(bars.iterrows()):
        if timestamp in by_time:
            pending.append((by_time[timestamp], i))

        fill_candidates = pending[:] if (allow_multiple or not active) else []
        for signal, signal_i in fill_candidates:
            # Signals are generated at bar close; no order may fill on that bar.
            if i <= signal_i:
                continue
            fill = pending_fill(signal, bar, cfg, i - signal_i)
            if fill is None:
                if signal.expiry_bars is not None and i - signal_i > signal.expiry_bars:
                    pending.remove((signal, signal_i))
                continue
            lots = risk_engine.size_position(balance, abs(fill.price - signal.stop_loss)) if risk_engine else 1.0
            if lots <= 0:
                pending.remove((signal, signal_i))
                continue
            active.append({"signal": signal, "entry_time": fill.time, "entry": fill.price,
                           "entry_i": i, "lots": lots, "risk": abs(fill.price - signal.stop_loss),
                           "mae": 0.0, "mfe": 0.0})
            pending.remove((signal, signal_i))
            if not allow_multiple:
                break

        for position in active[:]:
            direction = 1 if position["signal"].side == "long" else -1
            position["mae"] = min(position["mae"], (float(bar.low) - position["entry"]) * direction,
                                  (float(bar.high) - position["entry"]) * direction)
            position["mfe"] = max(position["mfe"], (float(bar.low) - position["entry"]) * direction,
                                  (float(bar.high) - position["entry"]) * direction)
            decision = protective_exit(position, bar, cfg)
            max_bars = cfg.get("engine", {}).get("max_bars_in_trade")
            if decision is None and max_bars is not None and i - position["entry_i"] >= int(max_bars):
                decision = ("time_stop", float(bar.close))
            if decision is None and i == len(bars) - 1:
                decision = ("eod", float(bar.close))
            if decision is None:
                continue
            reason, raw_exit = decision
            exit_price, gross, costs, net = close_position(position, bar, reason, float(raw_exit), cfg)
            point_value = float(cfg.get("costs", {}).get("point_value_per_lot", 1.0))
            risk = position["risk"] * point_value * position["lots"]
            signal = position["signal"]
            rows.append({
                "trade_id": len(rows) + 1, "strategy": strategy_name, "side": signal.side,
                "signal_time": signal.time, "entry_time": position["entry_time"],
                "entry_price": position["entry"], "exit_time": timestamp, "exit_price": exit_price,
                "exit_reason": reason, "lots": position["lots"], "sl_price": signal.stop_loss,
                "tp_price": signal.take_profit, "risk_amount": risk, "gross_pnl": gross,
                "costs": costs, "net_pnl": net, "r_multiple": net / risk if risk else 0.0,
                "mae": position["mae"] * point_value, "mfe": position["mfe"] * point_value,
                "bars_held": i - position["entry_i"], "meta": signal.meta,
            })
            balance += net
            if risk_engine:
                risk_engine.record(timestamp, net, balance)
            active.remove(position)

        balances.append(balance)
        unrealized.append(sum(mark_to_market(p, float(bar.close), cfg) for p in active))

    return BacktestResult(pd.DataFrame(rows, columns=TRADE_COLS),
                          equity_curve(bars.index, balances, unrealized),
                          cfg, strategy_name, params or {}, period)
