from .base import Signal, Strategy


class TrendMomentum(Strategy):
    name = "trend_momentum"

    def required_features(self):
        return ["atr_14", "ema_20", "ema_50", "adx_14"]

    def generate_signals(self, bars, feats):
        rr = float(self.params.get("rr", 2.0))
        adx_threshold = float(self.params.get("adx_threshold", 20.0))
        sl_atr = float(self.params.get("sl_atr", 1.5))
        out = []
        for i in range(1, len(bars)):
            row, prev = feats.iloc[i], feats.iloc[i - 1]
            atr = row.get("atr_14")
            if pd_is_na(atr) or atr <= 0 or row.get("adx_14", 0) < adx_threshold:
                continue
            close = float(bars.iloc[i].close)
            previous_close = float(bars.iloc[i - 1].close)
            long_setup = close > row.ema_20 > row.ema_50 and previous_close <= prev.ema_20
            short_setup = close < row.ema_20 < row.ema_50 and previous_close >= prev.ema_20
            if long_setup:
                stop = close - sl_atr * atr
                out.append(Signal(bars.index[i], "long", "market_next_open", None, stop,
                                  close + rr * (close - stop), None, {"strategy": self.name}))
            elif short_setup:
                stop = close + sl_atr * atr
                out.append(Signal(bars.index[i], "short", "market_next_open", None, stop,
                                  close - rr * (stop - close), None, {"strategy": self.name}))
        return out

    def param_space(self):
        return {"rr": [1.5, 2.0, 3.0], "adx_threshold": [18.0, 20.0, 25.0], "sl_atr": [1.0, 1.5, 2.0]}


def pd_is_na(value):
    return value != value
