from dataclasses import dataclass
import pandas as pd
from goldsys.strategies.base import Signal
@dataclass
class BacktestResult:
    trades: pd.DataFrame; equity: pd.Series; config_snapshot: dict; strategy: str; params: dict; period: tuple[str,str]
TRADE_COLS=["trade_id","strategy","side","signal_time","entry_time","entry_price","exit_time","exit_price","exit_reason","lots","sl_price","tp_price","risk_amount","gross_pnl","costs","net_pnl","r_multiple","mae","mfe","bars_held","meta"]
def run_backtest(bars, signals: list[Signal], cfg, strategy_name="strategy", params=None, period=("", "")):
    costs=cfg.get("costs",{}); equity0=cfg.get("engine",{}).get("initial_equity",10000); spread=costs.get("spread_points",.3); slip=costs.get("slippage_points",.1); pv=costs.get("point_value_per_lot",100); by_time={s.time:s for s in signals}; active=None; rows=[]; equity=[]; balance=equity0
    for i,(t,b) in enumerate(bars.iterrows()):
        if active is None and t in by_time and i+1<len(bars.index):
            s=by_time[t]; nt=bars.index[i+1]; entry=float(bars.iloc[i+1].open)+(spread/2+slip)*(1 if s.side=="long" else -1); risk=abs(entry-s.stop_loss); active={"s":s,"entry_time":nt,"entry":entry,"risk":risk,"entry_i":i+1,"mae":0.,"mfe":0.}
        if active and t>=active["entry_time"]:
            s=active["s"]; entry=active["entry"]; direction=1 if s.side=="long" else -1; active["mae"]=min(active["mae"],(b.low-entry)*direction,(b.high-entry)*direction); active["mfe"]=max(active["mfe"],(b.low-entry)*direction,(b.high-entry)*direction); sl=(b.low<=s.stop_loss) if s.side=="long" else (b.high>=s.stop_loss); tp=s.take_profit is not None and ((b.high>=s.take_profit) if s.side=="long" else (b.low<=s.take_profit)); reason=exitp=None
            if sl: reason,exitp="sl",s.stop_loss
            elif tp: reason,exitp="tp",s.take_profit
            elif i==len(bars)-1: reason,exitp="eod",float(b.close)
            if reason:
                exitp=float(exitp)-(spread/2+slip)*direction; gross=(exitp-entry)*direction*pv; c=spread*pv+costs.get("commission_per_lot",0); net=gross-c; rows.append({"trade_id":len(rows)+1,"strategy":strategy_name,"side":s.side,"signal_time":s.time,"entry_time":active["entry_time"],"entry_price":entry,"exit_time":t,"exit_price":exitp,"exit_reason":reason,"lots":1.,"sl_price":s.stop_loss,"tp_price":s.take_profit,"risk_amount":active["risk"]*pv,"gross_pnl":gross,"costs":c,"net_pnl":net,"r_multiple":net/(active["risk"]*pv) if active["risk"] else 0,"mae":active["mae"]*pv,"mfe":active["mfe"]*pv,"bars_held":i-active["entry_i"],"meta":s.meta}); balance+=net; active=None
        equity.append(balance)
    return BacktestResult(pd.DataFrame(rows,columns=TRADE_COLS),pd.Series(equity,index=bars.index),cfg,strategy_name,params or {},period)
