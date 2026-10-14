import pandas as pd
from .base import register_feature

@register_feature("volatility")
def volatility_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    prev = bars.close.shift(1)
    tr = pd.concat([(bars.high-bars.low).abs(), (bars.high-prev).abs(), (bars.low-prev).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14, min_periods=14).mean()
    return pd.DataFrame({"true_range": tr, "atr_14": atr, "atr_percentile_100": atr.rolling(100, min_periods=20).rank(pct=True), "range_atr_ratio": (bars.high-bars.low).div(atr), "realized_vol_20": bars.close.pct_change().rolling(20, min_periods=20).std()}, index=bars.index)
