import numpy as np


def _max_dd(equity):
    peak = np.maximum.accumulate(equity)
    return float(np.max((peak - equity) / peak) * 100) if len(equity) else 0.0


def monte_carlo(trades, initial_equity=10000.0, runs=200, seed=42, skip_rate=0.0):
    pnl = np.asarray(trades.net_pnl, dtype=float)
    rng = np.random.default_rng(seed)
    if not len(pnl):
        return {"runs": 0, "final_equity": {}, "max_drawdown_pct": {}, "probability_of_ruin": 0.0}
    finals, drawdowns = [], []
    for _ in range(int(runs)):
        sample = rng.choice(pnl, size=len(pnl), replace=True)
        if skip_rate:
            sample[rng.random(len(sample)) < skip_rate] = 0
        equity = initial_equity + np.cumsum(sample)
        finals.append(float(equity[-1]))
        drawdowns.append(_max_dd(equity))
    q = lambda values: {"p05": float(np.quantile(values, .05)), "median": float(np.quantile(values, .5)), "p95": float(np.quantile(values, .95))}
    return {"runs": int(runs), "final_equity": q(finals), "max_drawdown_pct": q(drawdowns),
            "probability_of_ruin": float(np.mean(np.asarray(finals) <= 0))}
