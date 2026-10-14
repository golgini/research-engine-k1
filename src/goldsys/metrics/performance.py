import pandas as pd
def performance(result):
    tr=result.trades; eq=result.equity; pnl=tr.net_pnl if not tr.empty else pd.Series(dtype=float); peak=eq.cummax(); dd=(eq/peak-1)*100; wins=pnl[pnl>0].sum(); losses=-pnl[pnl<0].sum()
    return {"net_profit":float(pnl.sum()),"trades":int(len(tr)),"win_rate":float((pnl>0).mean()) if len(pnl) else 0.,"profit_factor":float(wins/losses) if losses else float("inf"),"max_drawdown_pct":float(-dd.min()),"expectancy_r":float(tr.r_multiple.mean()) if not tr.empty else 0.,"final_equity":float(eq.iloc[-1]) if len(eq) else 0.}
