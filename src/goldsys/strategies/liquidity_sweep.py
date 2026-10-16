from .base import Signal, Strategy


class LiquiditySweep(Strategy):
    name = "liquidity_sweep"

    def required_features(self):
        return ["atr_14", "sweep_prev_high", "sweep_prev_low", "bullish_engulfing", "bearish_engulfing"]

    def generate_signals(self, bars, feats):
        rr = float(self.params.get("rr", 1.5))
        buffer_atr = float(self.params.get("buffer_atr", 0.15))
        out = []
        for i, timestamp in enumerate(bars.index):
            row = feats.iloc[i]
            atr = row.get("atr_14")
            if pd_is_na(atr) or atr <= 0:
                continue
            close, high, low = map(float, (bars.iloc[i].close, bars.iloc[i].high, bars.iloc[i].low))
            if bool(row.get("sweep_prev_low", False)) and bool(row.get("bullish_engulfing", False)):
                stop = low - buffer_atr * atr
                out.append(Signal(timestamp, "long", "market_next_open", None, stop,
                                  close + rr * (close - stop), None, {"strategy": self.name, "setup": "low_sweep"}))
            elif bool(row.get("sweep_prev_high", False)) and bool(row.get("bearish_engulfing", False)):
                stop = high + buffer_atr * atr
                out.append(Signal(timestamp, "short", "market_next_open", None, stop,
                                  close - rr * (stop - close), None, {"strategy": self.name, "setup": "high_sweep"}))
        return out

    def param_space(self):
        return {"rr": [1.0, 1.5, 2.0], "buffer_atr": [0.1, 0.15, 0.25]}


def pd_is_na(value):
    return value != value
