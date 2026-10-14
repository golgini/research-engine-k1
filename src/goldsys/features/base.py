from collections.abc import Callable
import pandas as pd
FeatureFn = Callable[[pd.DataFrame, dict], pd.DataFrame]
REGISTRY: dict[str, FeatureFn] = {}
def register_feature(name: str):
    def deco(fn: FeatureFn): REGISTRY[name] = fn; return fn
    return deco

@register_feature("core")
def core_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    x = bars; out = pd.DataFrame(index=x.index); close = x.close
    tr = pd.concat([(x.high-x.low), (x.high-close.shift()).abs(), (x.low-close.shift()).abs()], axis=1).max(axis=1)
    out["tr"] = tr; out["atr_14"] = tr.rolling(14, min_periods=14).mean()
    out["ret_1"] = close.pct_change(); out["realized_vol_20"] = out.ret_1.rolling(20, min_periods=20).std()
    out["ema_20"] = close.ewm(span=20, adjust=False).mean(); out["ema_50"] = close.ewm(span=50, adjust=False).mean()
    out["sma_200"] = close.rolling(200, min_periods=200).mean(); out["momentum_20"] = close.pct_change(20)
    out["hour"] = x.index.hour; out["weekday"] = x.index.weekday; out["month"] = x.index.month
    out["session"] = pd.Series("off", index=x.index); out.loc[(out.hour>=0)&(out.hour<7), "session"]="asia"; out.loc[(out.hour>=7)&(out.hour<12), "session"]="london"; out.loc[(out.hour>=12)&(out.hour<21), "session"]="ny"
    out["vwap_20"] = ((x.close*x.volume).rolling(20).sum()/x.volume.replace(0, pd.NA).rolling(20).sum()).fillna(close.rolling(20).mean())
    return out

def build_features(bars: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or {}; parts = [fn(bars, cfg) for fn in REGISTRY.values()]
    return pd.concat(parts, axis=1).loc[:, ~pd.concat(parts, axis=1).columns.duplicated()]
