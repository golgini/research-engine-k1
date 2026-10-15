import numpy as np
import pandas as pd

from goldsys.features.base import register_feature


def _indicators(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    high, low, close = bars.high, bars.low, bars.close
    prev_close = close.shift(1)
    tr = pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    params = cfg.get("regimes", {})
    atr_window = int(params.get("atr_window", 14))
    percentile_window = int(params.get("percentile_window", 100))
    atr = tr.rolling(atr_window, min_periods=atr_window).mean()
    atr_pct = atr.rolling(percentile_window, min_periods=atr_window).rank(pct=True)
    up, down = high.diff(), -low.diff()
    plus = up.where((up > down) & (up > 0), 0.0)
    minus = down.where((down > up) & (down > 0), 0.0)
    plus_di = 100 * plus.rolling(atr_window, min_periods=atr_window).sum() / atr.replace(0, np.nan) / atr_window
    minus_di = 100 * minus.rolling(atr_window, min_periods=atr_window).sum() / atr.replace(0, np.nan) / atr_window
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.rolling(atr_window, min_periods=atr_window).mean()
    ema_fast = close.ewm(span=20, adjust=False).mean()
    ema_slow = close.ewm(span=50, adjust=False).mean()
    slope = ema_fast.diff(int(params.get("slope_window", 5)))
    return pd.DataFrame({"regime_atr": atr, "regime_atr_percentile": atr_pct,
                         "regime_adx": adx, "regime_ema_slope_atr": slope.div(atr.replace(0, np.nan)),
                         "regime_ema_fast": ema_fast, "regime_ema_slow": ema_slow}, index=bars.index)


def label_regimes(bars: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Return past-only trend, volatility, and combined regime labels."""
    cfg = cfg or {}
    out = _indicators(bars, cfg)
    params = cfg.get("regimes", {})
    adx_threshold = float(params.get("adx_threshold", 20.0))
    slope_threshold = float(params.get("slope_threshold_atr", 0.02))
    low_vol = float(params.get("low_vol_percentile", 1 / 3))
    high_vol = float(params.get("high_vol_percentile", 2 / 3))
    trend = pd.Series("unknown", index=bars.index, dtype="object")
    valid = out.regime_adx.notna() & out.regime_ema_slope_atr.notna()
    trending = valid & (out.regime_adx >= adx_threshold) & (out.regime_ema_slope_atr.abs() >= slope_threshold)
    trend.loc[valid & ~trending] = "range"
    trend.loc[trending & (out.regime_ema_slope_atr > 0)] = "trend_up"
    trend.loc[trending & (out.regime_ema_slope_atr < 0)] = "trend_down"
    volatility = pd.Series("unknown", index=bars.index, dtype="object")
    volatility.loc[out.regime_atr_percentile.notna() & (out.regime_atr_percentile < low_vol)] = "lowvol"
    volatility.loc[out.regime_atr_percentile.notna() & (out.regime_atr_percentile > high_vol)] = "highvol"
    volatility.loc[out.regime_atr_percentile.notna() & volatility.eq("unknown")] = "normalvol"
    out["trend_regime"] = trend
    out["volatility_regime"] = volatility
    out["regime"] = trend.where(trend.eq("unknown"), trend + "_" + volatility)
    return out


@register_feature("regime")
def regime_features(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    return label_regimes(bars, cfg)
