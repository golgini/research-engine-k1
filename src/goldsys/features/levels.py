import pandas as pd
from .base import register_feature

@register_feature("levels")
def level_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    day=bars.index.normalize(); daily=bars.resample("1D").agg({"high":"max","low":"min","close":"last"}); prev=daily.shift(1); out=pd.DataFrame(index=bars.index)
    out["prev_day_high"]=day.map(prev.high); out["prev_day_low"]=day.map(prev.low); out["prev_day_close"]=day.map(prev.close)
    week=bars.resample("1W",label="left",closed="left").agg({"high":"max","low":"min","close":"last"}).shift(1); week_key=bars.index.tz_convert(None).to_period("W").start_time.tz_localize("UTC"); out["prev_week_high"]=week_key.map(week.high); out["prev_week_low"]=week_key.map(week.low)
    vol=bars.volume.replace(0,pd.NA); out["vwap_20"]=(bars.close*vol).rolling(20,min_periods=5).sum()/vol.rolling(20,min_periods=5).sum(); out["vwap_20"]=out.vwap_20.fillna(bars.close.rolling(20,min_periods=5).mean()); out["round_number_10"]=(bars.close/10).round()*10; out["distance_round_10"]=bars.close-out.round_number_10
    return out
