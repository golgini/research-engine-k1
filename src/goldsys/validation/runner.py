import json
from pathlib import Path

from goldsys.validation.gate import evaluate_gate
from goldsys.validation.monte_carlo import monte_carlo


def write_validation_report(result, cfg, output_dir, monte_carlo_runs=200):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    gate = evaluate_gate(result["metrics"], cfg)
    mc = monte_carlo(result["backtest"].trades, result["backtest"].equity.iloc[0], runs=monte_carlo_runs)
    payload = {"gate": gate, "monte_carlo": mc}
    (out / "gate.json").write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    return payload
