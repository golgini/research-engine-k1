from pathlib import Path
import csv
import pandas as pd

def _read_one(path: Path) -> pd.DataFrame:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:4096]
    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    has_header = any(x in sample.splitlines()[0].lower() for x in ("open", "close", "date", "time"))
    names = None if has_header else ["date", "time", "open", "high", "low", "close", "volume"]
    df = pd.read_csv(path, sep=dialect.delimiter, header=0 if has_header else None, names=names)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    aliases = {"o":"open", "h":"high", "l":"low", "c":"close", "vol":"volume", "tick_volume":"volume"}
    df = df.rename(columns={c: aliases.get(c, c) for c in df.columns})
    if "datetime" not in df and "date" in df and "time" in df:
        dt = df["date"].astype(str) + " " + df["time"].astype(str)
    else:
        candidate = next((c for c in ("datetime", "timestamp", "date", "time") if c in df), None)
        if candidate is None:
            raise ValueError(f"No datetime column in {path}")
        dt = df[candidate]
    df["time"] = pd.to_datetime(dt, errors="coerce", utc=True, format="mixed")
    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df]
    if missing: raise ValueError(f"Missing columns {missing} in {path}")
    if "volume" not in df: df["volume"] = float("nan")
    out = df[["time", *required, "volume"]].copy()
    for c in required + ["volume"]: out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.dropna(subset=["time", *required])

def load_csvs(raw_dir: str | Path, pattern: str = "*.csv") -> pd.DataFrame:
    files = sorted(Path(raw_dir).glob(pattern))
    if not files: raise FileNotFoundError(f"No CSV files found in {raw_dir}")
    df = pd.concat((_read_one(p) for p in files), ignore_index=True)
    df = df.sort_values("time").drop_duplicates("time", keep="last").set_index("time")
    df.index.name = "time"
    return df[["open", "high", "low", "close", "volume"]].astype(float)
