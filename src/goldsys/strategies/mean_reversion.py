from .base import Signal, Strategy


class MeanReversion(Strategy):
    name = "mean_reversion"

    def required_features(self):
        return ["atr_14", "vwap_20", "regime"]

    def generate_signals(self, bars, feats):
        extension = float(self.params.get("extension_atr", 1.5))
        stop_atr = float(self.params.get("stop_atr", 1.0))
        out = []
        for i, timestamp in enumerate(bars.index):
            row = feats.iloc[i]
            atr, vwap = row.get("atr_14"), row.get("vwap_20")
            if pd_is_na(atr) or pd_is_na(vwap) or atr <= 0 or row.get("trend_regime") not in {"range", "unknown"}:
                continue
            close = float(bars.iloc[i].close)
            if close < vwap - extension * atr:
                stop = close - stop_atr * atr
                out.append(Signal(timestamp, "long", "market_next_open", None, stop, float(vwap), None,
                                  {"strategy": self.name, "target": "vwap"}))
            elif close > vwap + extension * atr:
                stop = close + stop_atr * atr
                out.append(Signal(timestamp, "short", "market_next_open", None, stop, float(vwap), None,
                                  {"strategy": self.name, "target": "vwap"}))
        return out

    def param_space(self):
        return {"extension_atr": [1.0, 1.5, 2.0], "stop_atr": [0.75, 1.0, 1.5]}


def pd_is_na(value):
    return value != value
