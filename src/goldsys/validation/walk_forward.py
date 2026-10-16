import pandas as pd

from goldsys.engine.backtester import run_backtest
from goldsys.features.base import build_features
from goldsys.metrics.performance import performance


def walk_forward(bars, strategy_factory, cfg, windows):
    """Run fixed-parameter out-of-sample windows without refitting on future data."""
    rows = []
    for train_start, train_end, test_start, test_end in windows:
        train = bars.loc[pd.Timestamp(train_start, tz="UTC"):pd.Timestamp(train_end, tz="UTC")]
        test = bars.loc[pd.Timestamp(test_start, tz="UTC"):pd.Timestamp(test_end, tz="UTC")]
        strategy = strategy_factory()
        train_result = run_backtest(train, strategy.generate_signals(train, build_features(train, cfg)), cfg)
        test_result = run_backtest(test, strategy.generate_signals(test, build_features(test, cfg)), cfg)
        rows.append({"train_start": str(train_start), "test_start": str(test_start),
                     "train": performance(train_result), "test": performance(test_result)})
    return pd.DataFrame(rows)
