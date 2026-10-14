from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from goldsys.config import load_config

class HoldoutLockedError(RuntimeError): pass

def _unlock_flag(cfg: dict) -> Path:
    return Path(cfg.get("splits", {}).get("unlock_flag", "config/.holdout_unlocked"))

def get_period(df: pd.DataFrame, name: str, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or load_config(); periods = cfg["splits"]
    if name not in {"train", "validation", "holdout", "dev"}:
        raise ValueError(f"Unknown period {name!r}")
    if name == "holdout" and periods.get("holdout_locked", True) and not _unlock_flag(cfg).exists():
        raise HoldoutLockedError("Hold-out is locked until `goldsys holdout unlock --confirm`.")
    if name == "dev":
        return pd.concat([get_period(df, "train", cfg), get_period(df, "validation", cfg)]).sort_index()
    start, end = periods[name]
    return df.loc[pd.Timestamp(start, tz="UTC"):pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)]

def load_bars(timeframe: str, period: str, cfg: dict | None = None, root: str | Path = ".") -> pd.DataFrame:
    """Load one canonical parquet timeframe and return only an approved period."""
    cfg = cfg or load_config()
    path = Path(root) / "data" / "interim" / f"bars_{timeframe}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing canonical bars: {path}. Run `goldsys data ingest` first.")
    return get_period(pd.read_parquet(path), period, cfg)

def unlock_holdout(cfg: dict | None = None, reason: str = "manual research authorization", user: str | None = None) -> Path:
    cfg = cfg or load_config()
    flag = _unlock_flag(cfg); flag.parent.mkdir(parents=True, exist_ok=True); flag.write_text("unlocked\n", encoding="utf-8")
    log = Path("reports/holdout_access.log"); log.parent.mkdir(parents=True, exist_ok=True)
    who = user or __import__("getpass").getuser()
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()}\t{who}\t{reason}\n")
    return flag
