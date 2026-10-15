import pandas as pd

def forward_returns(bars: pd.DataFrame, event_mask: pd.Series, horizons=(1, 4, 24)) -> pd.DataFrame:
    out={}
    for n in horizons: out[f"fwd_{n}"]=bars.close.pct_change(n).shift(-n).where(event_mask)
    return pd.DataFrame(out,index=bars.index)
