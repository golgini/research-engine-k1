import pandas as pd
from .base import register_feature

@register_feature("sessions")
def session_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out=pd.DataFrame(index=bars.index); h=bars.index.hour
    out["session"]="off"; out.loc[(h>=0)&(h<7),"session"]="asia"; out.loc[(h>=7)&(h<12),"session"]="london"; out.loc[(h>=12)&(h<21),"session"]="ny"
    day=bars.index.normalize(); out["day_open"]=bars.groupby(day).open.transform("first"); out["session_open"]=bars.groupby([day,out.session]).open.transform("first"); out["session_high_so_far"]=bars.groupby([day,out.session]).high.cummax(); out["session_low_so_far"]=bars.groupby([day,out.session]).low.cummin()
    out["bars_since_session_open"]=bars.groupby([day,out.session]).cumcount(); asia=(out.session=="asia"); out["asian_range_high"]=bars.high.where(asia).groupby(day).transform("max"); out["asian_range_low"]=bars.low.where(asia).groupby(day).transform("min"); out["asian_range_size"]=out.asian_range_high-out.asian_range_low
    return out
