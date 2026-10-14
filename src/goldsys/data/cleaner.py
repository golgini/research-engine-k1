import pandas as pd

def clean_bars(bars: pd.DataFrame, atr_window: int = 100, bad_tick_multiple: float = 15) -> pd.DataFrame:
    x = bars.copy().sort_index()
    x = x[~x.index.duplicated(keep="last")]
    x = x[(x[["open","high","low","close"]] > 0).all(axis=1)]
    x["is_suspect"] = False
    x["true_range"] = (x.high - x.low).abs()
    atr = x.true_range.rolling(atr_window, min_periods=20).median()
    x.loc[atr.notna() & (x.true_range > bad_tick_multiple * atr), "is_suspect"] = True
    x = x.drop(columns="true_range")
    return x
