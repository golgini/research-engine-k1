from .base import Strategy, Signal
class SessionBreakout(Strategy):
    name = "session_breakout"
    def generate_signals(self, bars, feats):
        out=[]; day=bars.index.normalize()
        for _, ix in bars.groupby(day).groups.items():
            sub=bars.loc[ix]; asia=sub.between_time("00:00","06:59"); london=sub.between_time("07:00","11:59")
            if asia.empty or london.empty: continue
            hi,lo=asia.high.max(),asia.low.min(); risk=hi-lo; rr=self.params.get("rr",1.5)
            for t,row in london.iterrows():
                if row.close>hi and risk>0:
                    sl=hi-risk*.05; out.append(Signal(t,"long","market_next_open",None,sl,row.close+rr*(row.close-sl),None,{"strategy":self.name})); break
                if row.close<lo and risk>0:
                    sl=lo+risk*.05; out.append(Signal(t,"short","market_next_open",None,sl,row.close-rr*(sl-row.close),None,{"strategy":self.name})); break
        return out
    def param_space(self): return {"rr":[1.0,1.5,2.0]}
