import numpy as np
import pandas as pd
from .base import register_feature

@register_feature("trend")
def trend_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    h,l,c=bars.high,bars.low,bars.close; up=h.diff(); down=-l.diff(); plus=up.where((up>down)&(up>0),0.); minus=down.where((down>up)&(down>0),0.); tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.rolling(14,min_periods=14).mean(); pdi=100*plus.rolling(14).sum()/atr.replace(0,np.nan)/14; mdi=100*minus.rolling(14).sum()/atr.replace(0,np.nan)/14; dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan); out=pd.DataFrame(index=bars.index); out["ema_20"]=c.ewm(span=20,adjust=False).mean(); out["ema_50"]=c.ewm(span=50,adjust=False).mean(); out["sma_200"]=c.rolling(200,min_periods=200).mean(); out["ema_slope_20"]=out.ema_20.diff(5); out["adx_14"]=dx.rolling(14,min_periods=14).mean(); out["roc_20"]=c.pct_change(20); out["trend_flag"]=(out.ema_20>out.ema_50).astype("int8"); return out
