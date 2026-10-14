from goldsys.features.base import build_features
def test_features_are_aligned(bars):
    f=build_features(bars,{}); assert len(f)==len(bars); assert {"atr_14","ema_20","session"} <= set(f)
def test_strategy_signal_geometry(bars):
    from goldsys.strategies.registry import get_strategy
    s=get_strategy("session_breakout"); signals=s.generate_signals(bars,build_features(bars,{}))
    for x in signals: assert (x.side=="long" and x.stop_loss<x.take_profit) or (x.side=="short" and x.stop_loss>x.take_profit)
