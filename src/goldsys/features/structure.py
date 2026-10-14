import pandas as pd
from .base import register_feature

@register_feature("structure")
def structure_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    left,right=2,2; h,l,c=bars.high,bars.low,bars.close; out=pd.DataFrame(index=bars.index)
    center_h=h.shift(right); center_l=l.shift(right); window_h=h.shift(right).rolling(left+right+1,min_periods=left+right+1).max(); window_l=l.shift(right).rolling(left+right+1,min_periods=left+right+1).min()
    out["confirmed_swing_high"]=(center_h==window_h); out["confirmed_swing_low"]=(center_l==window_l); out["swing_high_price"]=center_h.where(out.confirmed_swing_high); out["swing_low_price"]=center_l.where(out.confirmed_swing_low); out["sweep_prev_high"]=(h>out.swing_high_price.ffill().shift(1))&(c<h); out["sweep_prev_low"]=(l<out.swing_low_price.ffill().shift(1))&(c>l.shift(1)); out["bullish_engulfing"]=(c>bars.open)&(c.shift(1)<bars.open.shift(1))&(c>=bars.open.shift(1))&(bars.open<=c.shift(1)); out["bearish_engulfing"]=(c<bars.open)&(c.shift(1)>bars.open.shift(1))&(c<=bars.open.shift(1))&(bars.open>=c.shift(1)); return out
