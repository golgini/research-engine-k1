import pandas as pd

from goldsys.features.base import build_features
from goldsys.strategies.registry import get_strategy, list_strategies


def test_strategy_registry_contains_four_baselines():
    assert list_strategies() == ["liquidity_sweep", "mean_reversion", "session_breakout", "trend_momentum"]


def test_strategies_emit_valid_geometry_on_synthetic_setups():
    idx = pd.date_range("2020-01-01", periods=80, freq="h", tz="UTC")
    close = pd.Series(100.0, index=idx)
    close.iloc[30:45] = [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86]
    close.iloc[45:] = 100
    bars = pd.DataFrame({"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 100.0}, index=idx)
    feats = build_features(bars, {"regimes": {"percentile_window": 20}})
    for name in list_strategies():
        signals = get_strategy(name).generate_signals(bars, feats)
        for signal in signals:
            assert signal.time in bars.index
            assert (signal.side == "long" and signal.stop_loss < signal.take_profit) or (signal.side == "short" and signal.stop_loss > signal.take_profit)


def test_strategy_params_are_exposed():
    for name in list_strategies():
        assert get_strategy(name).param_space()
