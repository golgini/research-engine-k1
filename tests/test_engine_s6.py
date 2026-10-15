import pandas as pd

from goldsys.engine.backtester import run_backtest
from goldsys.strategies.base import Signal


def _bars(rows):
    idx = pd.date_range("2020-01-01", periods=len(rows), freq="h", tz="UTC")
    return pd.DataFrame(rows, index=idx)


def _cfg(**engine):
    return {"costs": {"spread_points": 0.2, "slippage_points": 0.0,
                      "point_value_per_lot": 1.0, "commission_per_lot": 0.0,
                      "swap_long_per_lot_per_day": 1.0, "swap_short_per_lot_per_day": 2.0},
            "engine": {"initial_equity": 1000, "intrabar_conflict": "sl_first", **engine}}


def _signal(t, stop=98, target=104):
    return Signal(t, "long", "market_next_open", None, stop, target, None)


def test_sl_first_and_spread_cost():
    bars = _bars([{"open": 100, "high": 101, "low": 99, "close": 100},
                  {"open": 100, "high": 105, "low": 95, "close": 100}])
    result = run_backtest(bars, [_signal(bars.index[0])], _cfg())
    trade = result.trades.iloc[0]
    assert trade.exit_reason == "sl"
    assert trade.exit_price == 97.9
    assert trade.costs == 0.2


def test_gap_through_stop_and_swap():
    bars = _bars([{"open": 100, "high": 101, "low": 99, "close": 100},
                  {"open": 95, "high": 96, "low": 94, "close": 95},
                  {"open": 95, "high": 96, "low": 94, "close": 95}])
    result = run_backtest(bars, [_signal(bars.index[0])], _cfg())
    trade = result.trades.iloc[0]
    assert trade.exit_reason == "sl"
    assert trade.exit_price == 94.9


def test_market_order_does_not_fill_on_last_or_same_bar_close():
    bars = _bars([{"open": 100, "high": 110, "low": 90, "close": 105}])
    result = run_backtest(bars, [_signal(bars.index[0])], _cfg())
    assert result.trades.empty
