import json
from pathlib import Path
import pandas as pd
from .loader import detect_timeframe

def quality_report(bars: pd.DataFrame) -> dict:
    d = {"start": str(bars.index.min()), "end": str(bars.index.max()), "bars": int(len(bars)), "detected_timeframe": detect_timeframe(bars),
         "duplicates": int(bars.index.duplicated().sum()), "sorted": bool(bars.index.is_monotonic_increasing),
         "suspect_bars": int(bars.get("is_suspect", pd.Series(False, index=bars.index)).sum()),
         "volume_available": bool(bars.volume.notna().any()), "price_min": float(bars.low.min()), "price_max": float(bars.high.max()),
         "invalid_ohlc": int(bars.get("is_invalid_ohlc", pd.Series(False, index=bars.index)).sum()),
         "gap_after_count": int(bars.get("is_gap_after", pd.Series(False, index=bars.index)).sum())}
    return d

def save_quality(report: dict, path: str | Path) -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(report, indent=2), encoding="utf-8")

def save_quality_markdown(report: dict, path: str | Path) -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Data quality report", "", *[f"- **{k}:** {v}" for k, v in report.items()]]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
