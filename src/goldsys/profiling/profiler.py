from pathlib import Path
import json
import numpy as np
import pandas as pd
from goldsys.data.splits import get_period
from goldsys.features.base import build_features

def _group_stats(df: pd.DataFrame, key: pd.Series) -> list[dict]:
    rows=[]
    for group, x in df.assign(_key=key).groupby("_key", observed=True):
        r=x.ret.dropna(); rows.append({"group":str(group),"samples":int(len(r)),"mean_return":float(r.mean()) if len(r) else 0.,"std_return":float(r.std()) if len(r)>1 else 0.,"up_rate":float((r>0).mean()) if len(r) else 0.,"t_stat":float(r.mean()/r.std()*np.sqrt(len(r))) if len(r)>1 and r.std()>0 else 0.})
    return rows

def _asian_breakout(bars: pd.DataFrame) -> dict:
    rows=[]
    for day, x in bars.groupby(bars.index.normalize()):
        asia=x.between_time("00:00","06:59"); london=x.between_time("07:00","11:59")
        if asia.empty or london.empty: continue
        hi,lo=asia.high.max(),asia.low.min(); first=london[(london.high>hi)|(london.low<lo)]
        if first.empty: continue
        b=first.iloc[0]; rows.append("high" if b.high>hi and not b.low<lo else "low" if b.low<lo and not b.high>hi else "both")
    n=len(rows); return {"samples":n,"high_first_rate":rows.count("high")/n if n else 0.,"low_first_rate":rows.count("low")/n if n else 0.,"both_rate":rows.count("both")/n if n else 0.}

def profile_market(bars: pd.DataFrame, cfg: dict | None = None) -> dict:
    cfg=cfg or {}; x=bars.copy(); x["ret"]=x.close.pct_change(); feats=build_features(x,cfg); x=x.join(feats,rsuffix="_feature");
    result={"date_range":[str(x.index.min()),str(x.index.max())],"bars":len(x),"returns_by_hour":_group_stats(x,x.index.hour),"returns_by_weekday":_group_stats(x,x.index.weekday),"returns_by_month":_group_stats(x,x.index.month),"returns_by_session":_group_stats(x,x["session"]),"asian_breakout":_asian_breakout(x),"volatility_clustering":{"abs_return_autocorr_1":float(x.ret.abs().autocorr(1)) if len(x)>2 else 0.,"atr_autocorr_1":float(x.atr_14.autocorr(1)) if x.atr_14.notna().sum()>2 else 0.}}
    big=x[x["atr_14"].notna() & (x["true_range"]>2*x["atr_14"])]
    result["big_move_study"]={"samples":int(len(big)),"mean_next_return":float(x.ret.shift(-1).loc[big.index].mean()) if len(big) else 0.}
    result["candidate_hypotheses"]=sorted([{"name":f"hour_{r['group']}_directional_bias","effect_size":abs(r["mean_return"]),"t_stat":r["t_stat"],"samples":r["samples"]} for r in result["returns_by_hour"]],key=lambda z:z["effect_size"],reverse=True)[:10]
    return result

def run_profile(df: pd.DataFrame, cfg: dict, output_dir: str | Path = "reports/profile", hypotheses_path: str | Path = "docs/hypotheses.md") -> dict:
    dev=get_period(df,"dev",cfg); result=profile_market(dev,cfg); out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); (out/"profile_summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    rows=["# Candidate hypotheses", "", "| Hypothesis | Effect size | t-stat | Samples |", "|---|---:|---:|---:|"]+[f"| {r['name']} | {r['effect_size']:.6g} | {r['t_stat']:.2f} | {r['samples']} |" for r in result["candidate_hypotheses"]]
    h=Path(hypotheses_path); h.parent.mkdir(parents=True,exist_ok=True); h.open("a",encoding="utf-8").write("\n\n"+"\n".join(rows)+"\n")
    html=f"<html><head><title>Gold market profile</title></head><body><h1>Gold market profile</h1><p>Development period only: {result['date_range'][0]} to {result['date_range'][1]}</p><pre>{json.dumps(result,indent=2)}</pre></body></html>"; (out/"profile.html").write_text(html,encoding="utf-8"); return result
