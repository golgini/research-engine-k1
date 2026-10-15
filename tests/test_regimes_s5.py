import pandas as pd

from goldsys.regimes.rules import label_regimes
from goldsys.regimes.stats import regime_statistics


def test_regimes_are_past_only_and_have_combined_labels(bars):
    cfg = {"regimes": {"percentile_window": 20}}
    prefix = label_regimes(bars.iloc[:250], cfg)
    full = label_regimes(bars, cfg)
    cols = ["regime_atr", "regime_atr_percentile", "regime_adx", "regime_ema_slope_atr", "regime"]
    pd.testing.assert_frame_equal(prefix[cols].iloc[-1:], full[cols].iloc[249:250], check_dtype=False, check_names=False)
    assert {"trend_regime", "volatility_regime", "regime"} <= set(full.columns)


def test_regime_statistics_group_by_year_and_regime(bars):
    stats = regime_statistics(bars, {"regimes": {"percentile_window": 20}})
    assert {"year", "regime", "share", "avg_return", "avg_atr"} <= set(stats.columns)
