from pathlib import Path


def export_pine(strategy, output_dir="reports/export"):
    out = Path(output_dir) / strategy
    out.mkdir(parents=True, exist_ok=True)
    script = f"""//@version=5
strategy("{strategy}", overlay=true, process_orders_on_close=false)
// Generated signal placeholder: replace the condition with the frozen {strategy} rules.
longSignal = false
shortSignal = false
if longSignal
    strategy.entry("Long", strategy.long)
if shortSignal
    strategy.entry("Short", strategy.short)
alertcondition(longSignal, "Long signal", "Long signal")
alertcondition(shortSignal, "Short signal", "Short signal")
"""
    target = out / f"{strategy}.pine"
    target.write_text(script, encoding="utf-8")
    return target
