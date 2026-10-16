import math

import numpy as np
import pandas as pd


def _max_drawdown(eq):
    peak = eq.cummax()
    drawdown = eq / peak - 1
    end = drawdown.idxmin() if len(drawdown) else None
    start = eq.loc[:end].idxmax() if end is not None else None
    return float(-drawdown.min() * 100) if len(drawdown) else 0.0, drawdown, start, end


def performance(result):
    trades = result.trades
    equity = result.equity.dropna().astype(float)
    pnl = trades.net_pnl.astype(float) if not trades.empty else pd.Series(dtype=float)
    returns = equity.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    dd_pct, drawdown, dd_start, dd_end = _max_drawdown(equity)
    years = max((equity.index[-1] - equity.index[0]).total_seconds() / (365.25 * 86400), 1 / 365.25) if len(equity) > 1 else 1 / 365.25
    initial = float(equity.iloc[0]) if len(equity) else 0.0
    final = float(equity.iloc[-1]) if len(equity) else 0.0
    cagr = (final / initial) ** (1 / years) - 1 if initial > 0 and final >= 0 else 0.0
    annual_factor = math.sqrt(365.25 * 24) if len(equity) > 1 else 0.0
    mean_ret = float(returns.mean()) if len(returns) else 0.0
    vol = float(returns.std(ddof=1) * annual_factor) if len(returns) > 1 else 0.0
    downside = returns[returns < 0]
    sharpe = float(mean_ret / returns.std(ddof=1) * annual_factor) if len(returns) > 1 and returns.std(ddof=1) > 0 else 0.0
    sortino = float(mean_ret / downside.std(ddof=1) * annual_factor) if len(downside) > 1 and downside.std(ddof=1) > 0 else 0.0
    wins, losses = pnl[pnl > 0].sum(), -pnl[pnl < 0].sum()
    bars = len(equity)
    bars_held = trades.bars_held.sum() if not trades.empty and "bars_held" in trades else 0
    streak = best_streak = 0
    for value in pnl:
        streak = streak + 1 if value < 0 else 0
        best_streak = max(best_streak, streak)
    monthly = equity.resample("ME").last().pct_change().dropna() if len(equity) else pd.Series(dtype=float)
    return {
        "net_profit": float(pnl.sum()), "trades": int(len(trades)),
        "cagr": float(cagr), "annualized_return": float(cagr), "annualized_volatility": vol,
        "sharpe": sharpe, "sortino": sortino, "calmar": float(cagr / (dd_pct / 100)) if dd_pct else 0.0,
        "max_drawdown_pct": dd_pct,
        "max_drawdown_duration_bars": int((dd_end - dd_start).total_seconds() / 3600) if dd_start is not None and dd_end is not None else 0,
        "profit_factor": float(wins / losses) if losses else None,
        "win_rate": float((pnl > 0).mean()) if len(pnl) else 0.0,
        "avg_win": float(pnl[pnl > 0].mean()) if (pnl > 0).any() else 0.0,
        "avg_loss": float(pnl[pnl < 0].mean()) if (pnl < 0).any() else 0.0,
        "payoff": float(pnl[pnl > 0].mean() / -pnl[pnl < 0].mean()) if (pnl > 0).any() and (pnl < 0).any() else 0.0,
        "expectancy_r": float(trades.r_multiple.mean()) if not trades.empty else 0.0,
        "trades_per_year": float(len(trades) / years), "exposure_pct": float(bars_held / bars * 100) if bars else 0.0,
        "longest_losing_streak": int(best_streak), "best_trade": float(pnl.max()) if len(pnl) else 0.0,
        "worst_trade": float(pnl.min()) if len(pnl) else 0.0,
        "mae_mean": float(trades.mae.mean()) if not trades.empty else 0.0,
        "mfe_mean": float(trades.mfe.mean()) if not trades.empty else 0.0,
        "ulcer_index": float(np.sqrt(np.mean((drawdown * 100) ** 2))) if len(drawdown) else 0.0,
        "final_equity": final,
        "monthly_returns": {str(k.date()): float(v) for k, v in monthly.items()},
    }
