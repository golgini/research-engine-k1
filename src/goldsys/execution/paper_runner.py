from pathlib import Path
import json

from goldsys.engine.backtester import run_backtest
from goldsys.features.base import build_features
from goldsys.strategies.registry import get_strategy


def replay_paper(bars, strategy_name, cfg, params=None):
    """Replay bars through the same signal and broker path as backtesting."""
    strategy = get_strategy(strategy_name, params or {})
    features = build_features(bars, cfg)
    signals = strategy.generate_signals(bars, features)
    return run_backtest(bars, signals, cfg, strategy_name=strategy_name, params=params or {}, period=("paper", ""))


def write_paper_log(result, output_dir="reports/paper"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.trades.to_csv(out / "trade_log.csv", index=False)
    summary = {"strategy": result.strategy, "trades": int(len(result.trades)),
               "final_equity": float(result.equity.iloc[-1]) if len(result.equity) else 0.0}
    (out / "daily_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
