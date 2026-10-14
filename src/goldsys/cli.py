from pathlib import Path
import json
import pandas as pd
import typer
from goldsys import __version__
from goldsys.config import load_config
from goldsys.data.loader import load_csvs, detect_timeframe
from goldsys.data.cleaner import clean_bars, flag_gaps
from goldsys.data.resampler import resample_bars
from goldsys.data.quality import quality_report, save_quality, save_quality_markdown
from goldsys.data.splits import unlock_holdout
from goldsys.features.base import build_features
from goldsys.strategies.registry import list_strategies
app=typer.Typer(help="XAUUSD research and strategy system")
data_app=typer.Typer(); app.add_typer(data_app,name="data")
holdout_app=typer.Typer(); app.add_typer(holdout_app,name="holdout")
@app.command()
def version(): typer.echo(__version__)
@data_app.command("ingest")
def ingest(config: str="config/config.yaml", timeframe: str="M1"):
    cfg=load_config(config); bars=flag_gaps(clean_bars(load_csvs(cfg["data"]["raw_dir"],cfg["data"]["file_glob"]),bad_tick_multiple=cfg["data"]["bad_tick_atr_multiple"]),cfg["data"]["max_gap_minutes_intraday"]); detected=detect_timeframe(bars); target=detected if timeframe.lower()=="auto" else timeframe; out=resample_bars(bars,target); Path("data/interim").mkdir(parents=True,exist_ok=True); out.to_parquet(f"data/interim/bars_{target}.parquet"); typer.echo(f"detected {detected}; wrote {len(out):,} canonical {target} bars")
@data_app.command("quality")
def quality(config: str="config/config.yaml", timeframe: str="M1"):
    cfg=load_config(config); p=Path(f"data/interim/bars_{timeframe}.parquet"); bars=pd.read_parquet(p) if p.exists() else resample_bars(flag_gaps(clean_bars(load_csvs(cfg["data"]["raw_dir"])),cfg["data"]["max_gap_minutes_intraday"]),timeframe); r=quality_report(bars); save_quality(r,"reports/quality.json"); save_quality_markdown(r,"reports/quality.md"); typer.echo(json.dumps(r,indent=2))
@app.command("strategies")
def strategies(): typer.echo("\n".join(list_strategies()))
@app.command("features")
def features(timeframe: str="H1", config: str="config/config.yaml"):
    cfg=load_config(config); bars=pd.read_parquet(f"data/interim/bars_{timeframe}.parquet"); f=build_features(bars,cfg); Path("data/processed").mkdir(parents=True,exist_ok=True); f.to_parquet(f"data/processed/features_{timeframe}.parquet"); typer.echo(f"wrote {f.shape[1]} features")
@holdout_app.command("unlock")
def holdout_unlock(confirm: bool=False, reason: str="manual research authorization"):
    if not confirm: raise typer.BadParameter("Pass --confirm to unlock the hold-out")
    unlock_holdout(load_config(), reason=reason); typer.echo("hold-out unlocked and access logged")

if __name__ == "__main__":
    app()
