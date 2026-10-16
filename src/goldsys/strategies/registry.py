from .session_breakout import SessionBreakout
from .trend_momentum import TrendMomentum
from .mean_reversion import MeanReversion
from .liquidity_sweep import LiquiditySweep

_REGISTRY={"session_breakout":SessionBreakout,"trend_momentum":TrendMomentum,
           "mean_reversion":MeanReversion,"liquidity_sweep":LiquiditySweep}
def get_strategy(name, params=None):
    if name not in _REGISTRY: raise KeyError(f"Unknown strategy {name}; choose {sorted(_REGISTRY)}")
    return _REGISTRY[name](params)
def list_strategies(): return sorted(_REGISTRY)
