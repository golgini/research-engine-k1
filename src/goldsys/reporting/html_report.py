import html
import json
from pathlib import Path

from goldsys.metrics.performance import performance


def write_backtest_report(result, output_dir: str | Path) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    metrics = performance(result)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding="utf-8")
    result.trades.to_csv(out / "trades.csv", index=False)
    rows = "".join(f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>" for k, v in metrics.items() if k != "monthly_returns")
    monthly = "".join(f"<tr><td>{html.escape(k)}</td><td>{v:.6f}</td></tr>" for k, v in metrics["monthly_returns"].items())
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Backtest report</title>
<style>body{{font:14px sans-serif;max-width:1100px;margin:2rem auto}}table{{border-collapse:collapse}}th,td{{border:1px solid #ccc;padding:.35rem .6rem;text-align:left}}</style>
</head><body><h1>Backtest report: {html.escape(result.strategy)}</h1>
<h2>Metrics</h2><table>{rows}</table><h2>Monthly returns</h2><table><tr><th>Month</th><th>Return</th></tr>{monthly}</table>
<p>Trades are available in <code>trades.csv</code>; machine-readable metrics are in <code>metrics.json</code>.</p></body></html>"""
    (out / "report.html").write_text(page, encoding="utf-8")
    return metrics
