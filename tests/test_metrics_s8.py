from types import SimpleNamespace

import pandas as pd
import pytest

from goldsys.metrics.performance import performance
from goldsys.reporting.html_report import write_backtest_report


def test_metrics_match_hand_computed_values(tmp_path):
    idx = pd.date_range("2020-01-01", periods=4, freq="h", tz="UTC")
    trades = pd.DataFrame({"net_pnl": [10.0, -5.0], "r_multiple": [1.0, -0.5],
                           "bars_held": [1, 1], "mae": [-2.0, -3.0], "mfe": [12.0, 4.0]})
    result = SimpleNamespace(trades=trades, equity=pd.Series([100, 110, 105, 105], index=idx), strategy="synthetic")
    metrics = performance(result)
    assert metrics["net_profit"] == 5.0
    assert metrics["trades"] == 2
    assert metrics["win_rate"] == 0.5
    assert metrics["max_drawdown_pct"] == pytest.approx(4.545454545454546)
    assert metrics["expectancy_r"] == 0.25
    write_backtest_report(result, tmp_path)
    assert (tmp_path / "report.html").exists()
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "trades.csv").exists()
