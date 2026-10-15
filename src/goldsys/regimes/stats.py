import pandas as pd

from .rules import label_regimes


def regime_statistics(bars: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Summarise regime share, return, and ATR by calendar year."""
    labels = label_regimes(bars, cfg)
    data = pd.DataFrame({"regime": labels.regime, "return": bars.close.pct_change(), "atr": labels.regime_atr}, index=bars.index)
    data["year"] = data.index.year
    stats = (data[data.regime.ne("unknown")]
             .groupby(["year", "regime"], observed=True)
             .agg(samples=("return", "count"), avg_return=("return", "mean"), avg_atr=("atr", "mean"))
             .reset_index())
    counts = stats.groupby("year")["samples"].transform("sum")
    stats["share"] = stats["samples"] / counts
    return stats[["year", "regime", "samples", "share", "avg_return", "avg_atr"]]
