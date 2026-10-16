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
from goldsys.data.splits import unlock_holdout, get_period
from goldsys.features.base import build_features
from goldsys.strategies.registry import list_strategies, get_strategy
from goldsys.engine.backtester import run_backtest
from goldsys.reporting.html_report import write_backtest_report
from goldsys.validation.gate import evaluate_gate
from goldsys.validation.monte_carlo import monte_carlo
from goldsys.ml.dataset import build_signal_dataset
from goldsys.ml.rule_discovery import discover_rules
from goldsys.ml.filters import rules_markdown
from goldsys.validation.final_test import freeze_candidate, run_final_test
from goldsys.execution.paper_runner import replay_paper, write_paper_log
from goldsys.execution.mt5_spec import export_mt5
from goldsys.execution.pine_export import export_pine
from goldsys.regimes.stats import regime_statistics
app=typer.Typer(help="XAUUSD research and strategy system")
data_app=typer.Typer(); app.add_typer(data_app,name="data")
holdout_app=typer.Typer(); app.add_typer(holdout_app,name="holdout")
profile_app=typer.Typer(); app.add_typer(profile_app,name="profile")
regime_app=typer.Typer(); app.add_typer(regime_app,name="regimes")
backtest_app=typer.Typer(); app.add_typer(backtest_app,name="backtest")
validate_app=typer.Typer(); app.add_typer(validate_app,name="validate")
ml_app=typer.Typer(); app.add_typer(ml_app,name="ml")
final_app=typer.Typer(); app.add_typer(final_app,name="final")
execution_app=typer.Typer(); app.add_typer(execution_app,name="execution")
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
@profile_app.command("run")
def profile_run(timeframe: str="H1", config: str="config/config.yaml"):
    from goldsys.profiling.profiler import run_profile
    cfg=load_config(config); bars=pd.read_parquet(f"data/interim/bars_{timeframe}.parquet"); result=run_profile(bars,cfg); typer.echo(f"profiled dev period: {result['date_range'][0]} to {result['date_range'][1]}")
@regime_app.command("run")
def regimes_run(timeframe: str="H1", config: str="config/config.yaml"):
    cfg=load_config(config); bars=pd.read_parquet(f"data/interim/bars_{timeframe}.parquet")
    out=regime_statistics(bars, cfg); Path("reports/regimes").mkdir(parents=True, exist_ok=True); out.to_csv(f"reports/regimes/{timeframe}_stats.csv", index=False)
    typer.echo(f"wrote {len(out)} regime/year rows")
@backtest_app.command("run")
def backtest_run(strategy: str, period: str="dev", timeframe: str="H1", config: str="config/config.yaml"):
    cfg=load_config(config); bars=get_period(pd.read_parquet(f"data/interim/bars_{timeframe}.parquet"), period, cfg)
    feats=build_features(bars, cfg); instance=get_strategy(strategy); signals=instance.generate_signals(bars, feats)
    result=run_backtest(bars, signals, cfg, strategy_name=strategy, period=(period, timeframe))
    stamp=pd.Timestamp.utcnow().strftime("%Y%m%d_%H%M%S"); out=Path("reports/backtests")/f"{strategy}_{stamp}"
    metrics=write_backtest_report(result, out); typer.echo(f"wrote {out} ({metrics['trades']} trades)")
@validate_app.command("run")
def validate_run(strategy: str, config: str="config/config.yaml", timeframe: str="H1"):
    cfg=load_config(config); bars=get_period(pd.read_parquet(f"data/interim/bars_{timeframe}.parquet"), "dev", cfg)
    instance=get_strategy(strategy); signals=instance.generate_signals(bars, build_features(bars, cfg))
    result=run_backtest(bars, signals, cfg, strategy_name=strategy, period=("dev", timeframe))
    from goldsys.metrics.performance import performance
    metrics=performance(result); gate=evaluate_gate(metrics, cfg); mc=monte_carlo(result.trades, result.equity.iloc[0], runs=cfg.get("validation",{}).get("monte_carlo_runs",200), seed=cfg.get("project",{}).get("seed",42))
    out=Path("reports/validation")/strategy; out.mkdir(parents=True, exist_ok=True); (out/"gate.json").write_text(json.dumps({"gate":gate,"monte_carlo":mc},indent=2,allow_nan=False),encoding="utf-8")
    typer.echo(f"{'PASS' if gate['passed'] else 'FAIL'}: wrote {out/'gate.json'}")
@ml_app.command("discover")
def ml_discover(strategy: str, config: str="config/config.yaml", timeframe: str="H1"):
    cfg=load_config(config); bars=get_period(pd.read_parquet(f"data/interim/bars_{timeframe}.parquet"), "dev", cfg)
    feats=build_features(bars, cfg); instance=get_strategy(strategy); signals=instance.generate_signals(bars, feats)
    result=run_backtest(bars, signals, cfg, strategy_name=strategy, period=("dev", timeframe))
    dataset=build_signal_dataset(signals, feats, result.trades)
    discovered=discover_rules(dataset, **cfg.get("ml", {})) if not dataset.empty else {"accepted":False,"rules":[],"best_auc":0.5}
    out=Path("reports/ml")/strategy; out.mkdir(parents=True, exist_ok=True); (out/"rules.md").write_text(rules_markdown(discovered),encoding="utf-8")
    typer.echo(f"{'accepted' if discovered['accepted'] else 'rejected'}: wrote {out/'rules.md'}")
@final_app.command("freeze")
def final_freeze(strategy: str, params: str="{}", config: str="config/config.yaml"):
    cfg=load_config(config); target,digest=freeze_candidate(strategy, json.loads(params), cfg)
    typer.echo(f"froze {target} ({digest})")
@final_app.command("test")
def final_test(strategy: str, params: str="{}", timeframe: str="H1", config: str="config/config.yaml", confirm: bool=False):
    if not confirm: raise typer.BadParameter("Pass --confirm to authorize the one-shot holdout test")
    cfg=load_config(config); bars=pd.read_parquet(f"data/interim/bars_{timeframe}.parquet")
    result,metrics=run_final_test(bars, strategy, cfg, json.loads(params))
    out=Path("reports/final")/strategy; out.mkdir(parents=True, exist_ok=True); (out/"metrics.json").write_text(json.dumps(metrics,indent=2,allow_nan=False),encoding="utf-8")
    typer.echo(f"wrote {out/'metrics.json'} ({metrics['trades']} trades)")
@execution_app.command("export")
def execution_export(strategy: str, params: str="{}"):
    export_mt5(strategy, json.loads(params)); export_pine(strategy)
    typer.echo(f"wrote execution exports for {strategy}")
@execution_app.command("paper")
def execution_paper(strategy: str, timeframe: str="H1", config: str="config/config.yaml", params: str="{}"):
    cfg=load_config(config); bars=get_period(pd.read_parquet(f"data/interim/bars_{timeframe}.parquet"), "dev", cfg)
    result=replay_paper(bars, strategy, cfg, json.loads(params)); summary=write_paper_log(result)
    typer.echo(f"paper replay complete: {summary['trades']} trades")
@holdout_app.command("unlock")
def holdout_unlock(confirm: bool=False, reason: str="manual research authorization"):
    if not confirm: raise typer.BadParameter("Pass --confirm to unlock the hold-out")
    unlock_holdout(load_config(), reason=reason); typer.echo("hold-out unlocked and access logged")

if __name__ == "__main__":
    app()
