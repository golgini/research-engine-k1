from pathlib import Path


def export_mt5(strategy, params=None, output_dir="reports/export"):
    out = Path(output_dir) / strategy
    out.mkdir(parents=True, exist_ok=True)
    params = params or {}
    inputs = "\n".join(f"- {key}: {value}" for key, value in params.items()) or "- No custom parameters"
    spec = f"""# MT5 EA specification: {strategy}

## Inputs

{inputs}

## Execution rules

- Generate signals only from completed bars.
- Enter at the next available market open.
- Apply configured spread, slippage, commission, and risk sizing.
- Respect stop loss, take profit, session, and drawdown limits.
- Paper-test before any live deployment.
"""
    (out / "EA_SPEC.md").write_text(spec, encoding="utf-8")
    skeleton = f"""//+------------------------------------------------------------------+
// {strategy} generated skeleton. Rule logic is intentionally pseudocode.
//+------------------------------------------------------------------+
#property strict
input double RiskPercent = 0.5;
// OnNewBar(): calculate completed-bar features and evaluate {strategy}.
// If signal passes risk limits, send an order with SL/TP and log the result.
"""
    (out / f"{strategy}.mq5").write_text(skeleton, encoding="utf-8")
    return out
