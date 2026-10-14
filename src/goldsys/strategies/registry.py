from .session_breakout import SessionBreakout
_REGISTRY={"session_breakout":SessionBreakout}
def get_strategy(name, params=None):
    if name not in _REGISTRY: raise KeyError(f"Unknown strategy {name}; choose {sorted(_REGISTRY)}")
    return _REGISTRY[name](params)
def list_strategies(): return sorted(_REGISTRY)
