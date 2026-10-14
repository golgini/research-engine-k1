import json
from pathlib import Path
import pandas as pd

def quality_report(bars: pd.DataFrame) -> dict:
    d = {"start": str(bars.index.min()), "end": str(bars.index.max()), "bars": int(len(bars)),
         "duplicates": int(bars.index.duplicated().sum()), "sorted": bool(bars.index.is_monotonic_increasing),
         "suspect_bars": int(bars.get("is_suspect", pd.Series(False, index=bars.index)).sum()),
         "volume_available": bool(bars.volume.notna().any()), "price_min": float(bars.low.min()), "price_max": float(bars.high.max())}
    return d

def save_quality(report: dict, path: str | Path) -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(report, indent=2), encoding="utf-8")
