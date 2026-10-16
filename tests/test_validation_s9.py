from types import SimpleNamespace

import pandas as pd

from goldsys.metrics.performance import performance
from goldsys.validation.gate import evaluate_gate
from goldsys.validation.monte_carlo import monte_carlo
from goldsys.validation.sensitivity import sensitivity
from goldsys.validation.cost_stress import cost_stress


def test_gate_passes_and_fails_expected_cases():
    good = {"trades": 25, "profit_factor": 1.5, "max_drawdown_pct": 10}
    bad = {"trades": 2, "profit_factor": 0.8, "max_drawdown_pct": 40}
    assert evaluate_gate(good, {})["passed"]
    assert not evaluate_gate(bad, {})["passed"]


def test_monte_carlo_is_seeded_and_bounded():
    trades = pd.DataFrame({"net_pnl": [10, -5, 8, -2]})
    a = monte_carlo(trades, runs=50, seed=7)
    b = monte_carlo(trades, runs=50, seed=7)
    assert a == b
    assert 0 <= a["probability_of_ruin"] <= 1


def test_sensitivity_returns_best_first():
    rows = sensitivity({"rr": [1, 2]}, lambda params: {"profit_factor": params["rr"], "trades": 10})
    assert rows[0]["value"] == 2


def test_gate_uses_real_performance_metrics():
    idx = pd.date_range("2020-01-01", periods=3, freq="h", tz="UTC")
    result = SimpleNamespace(trades=pd.DataFrame({"net_pnl": [5.0], "r_multiple": [1.0], "bars_held": [1], "mae": [0], "mfe": [5]}),
                             equity=pd.Series([100, 105, 105], index=idx))
    metrics = performance(result)
    assert evaluate_gate({**metrics, "trades": 25}, {"validation": {"gate": {"min_trades": 20}}})["passed"]


def test_cost_stress_does_not_mutate_config():
    cfg = {"costs": {"spread_points": 1.0, "slippage_points": 1.0}}
    rows = cost_stress(cfg, lambda stressed: {"net_profit": -stressed["costs"]["spread_points"]})
    assert rows[-1]["net_profit"] < rows[0]["net_profit"]
    assert cfg["costs"]["spread_points"] == 1.0
