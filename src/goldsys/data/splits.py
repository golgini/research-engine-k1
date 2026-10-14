from pathlib import Path
import pandas as pd
from goldsys.config import load_config

class HoldoutLockedError(RuntimeError): pass

def get_period(df: pd.DataFrame, name: str, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or load_config(); periods = cfg["splits"]
    if name == "holdout" and periods.get("holdout_locked", True) and not Path("config/.holdout_unlocked").exists():
        raise HoldoutLockedError("Hold-out is locked until `goldsys holdout unlock --confirm`.")
    if name == "dev":
        return pd.concat([get_period(df, "train", cfg), get_period(df, "validation", cfg)]).sort_index()
    start, end = periods[name]
    return df.loc[pd.Timestamp(start, tz="UTC"):pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)]
