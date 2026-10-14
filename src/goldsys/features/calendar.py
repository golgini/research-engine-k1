import pandas as pd
from .base import register_feature

@register_feature("calendar")
def calendar_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    idx=bars.index; out=pd.DataFrame(index=idx); out["hour"]=idx.hour; out["weekday"]=idx.weekday; out["month"]=idx.month; out["day_of_month"]=idx.day; out["is_month_start"]=(idx.day<=3); out["is_friday"]=(idx.weekday==4); return out
