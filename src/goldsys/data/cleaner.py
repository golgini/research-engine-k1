import pandas as pd

def clean_bars(bars: pd.DataFrame, atr_window: int = 100, bad_tick_multiple: float = 15) -> pd.DataFrame:
    x = bars.copy().sort_index()
    x = x[~x.index.duplicated(keep="last")]
    x = x[(x[["open","high","low","close"]] > 0).all(axis=1)]
    x["is_invalid_ohlc"] = (x.high < x[["open", "close"]].max(axis=1)) | (x.low > x[["open", "close"]].min(axis=1))
    x.loc[x["is_invalid_ohlc"], "high"] = x.loc[x["is_invalid_ohlc"], ["open", "high", "low", "close"]].max(axis=1)
    x.loc[x["is_invalid_ohlc"], "low"] = x.loc[x["is_invalid_ohlc"], ["open", "high", "low", "close"]].min(axis=1)
    x["is_suspect"] = False
    x["true_range"] = (x.high - x.low).abs()
    atr = x.true_range.rolling(atr_window, min_periods=20).median()
    x.loc[atr.notna() & (x.true_range > bad_tick_multiple * atr), "is_suspect"] = True
    x = x.drop(columns="true_range")
    return x

def flag_gaps(bars: pd.DataFrame, max_gap_minutes: int = 60) -> pd.DataFrame:
    x = bars.copy()
    gap = x.index.to_series().diff().dt.total_seconds().div(60)
    weekend = x.index.to_series().shift(-1).dt.weekday.ge(5) | x.index.to_series().dt.weekday.ge(5)
    x["is_gap_after"] = (gap > max_gap_minutes) & ~weekend.fillna(False)
    return x
