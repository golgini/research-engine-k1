import pandas as pd

_FREQ = {"M1":"1min", "M5":"5min", "M15":"15min", "M30":"30min", "H1":"1h", "H4":"4h", "D1":"1D", "W1":"1W"}

def resample_bars(bars: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    freq = _FREQ.get(timeframe.upper(), timeframe)
    agg = {"open":"first", "high":"max", "low":"min", "close":"last", "volume":"sum"}
    if "is_suspect" in bars: agg["is_suspect"] = "max"
    out = bars.resample(freq, label="left", closed="left").agg(agg).dropna(subset=["open","high","low","close"])
    return out
