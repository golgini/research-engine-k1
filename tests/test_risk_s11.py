import pandas as pd

from goldsys.risk.limits import RiskLimits
from goldsys.risk.portfolio import combine_equity
from goldsys.risk.sizing import fixed_fractional_lots


def test_fixed_fractional_sizing_rounds_and_rejects_oversized_minimum():
    cfg = {"risk": {"risk_per_trade_pct": 1, "min_lot": 0.01, "lot_step": 0.01, "max_lot": 5},
           "costs": {"point_value_per_lot": 100}}
    assert fixed_fractional_lots(10000, 1, cfg) == 1.0
    assert fixed_fractional_lots(100, 100, cfg) == 0.0


def test_limits_trigger_daily_cap_and_drawdown_halt():
    limits = RiskLimits({"daily_loss_cap_pct": 2, "max_drawdown_pct": 10, "max_open_positions": 1})
    t = pd.Timestamp("2020-01-01", tz="UTC")
    assert limits.can_trade(t, 1000, 0)
    limits.record(t, -25, 975)
    assert not limits.can_trade(t, 975, 0)
    limits.record(t + pd.Timedelta(days=1), -100, 875)
    assert not limits.can_trade(t + pd.Timedelta(days=1), 875, 0)


def test_portfolio_combiner_returns_combined_curve_and_correlation():
    idx = pd.date_range("2020-01-01", periods=3, freq="h", tz="UTC")
    frame, corr = combine_equity({"a": pd.Series([100, 101, 102], index=idx),
                                  "b": pd.Series([50, 49, 51], index=idx)})
    assert frame["combined"].iloc[-1] == 153
    assert corr.loc["a", "b"] <= 1
