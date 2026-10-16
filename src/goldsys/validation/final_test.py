import hashlib
import json
from pathlib import Path

import yaml

from goldsys.data.splits import get_period
from goldsys.engine.backtester import run_backtest
from goldsys.features.base import build_features
from goldsys.metrics.performance import performance


def freeze_candidate(strategy, params, cfg, output_dir="config/frozen"):
    payload = {"strategy": strategy, "params": params or {}, "config": cfg}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    document = {"strategy": strategy, "params": params or {}, "config_hash": digest}
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{strategy}.yaml"
    target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return target, digest


def run_final_test(bars, strategy_name, cfg, params=None):
    holdout = get_period(bars, "holdout", cfg)
    from goldsys.strategies.registry import get_strategy
    instance = get_strategy(strategy_name, params or {})
    features = build_features(holdout, cfg)
    signals = instance.generate_signals(holdout, features)
    result = run_backtest(holdout, signals, cfg, strategy_name=instance.name, params=params or {}, period=("holdout", ""))
    return result, performance(result)
