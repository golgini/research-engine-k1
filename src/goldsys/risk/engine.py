from .limits import RiskLimits
from .sizing import fixed_fractional_lots


class RiskEngine:
    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.limits = RiskLimits(self.cfg.get("risk", {}))

    def size_position(self, equity, stop_distance):
        return fixed_fractional_lots(equity, stop_distance, self.cfg)

    def can_trade(self, timestamp, equity, open_positions=0):
        return self.limits.can_trade(timestamp, equity, open_positions)

    def record(self, timestamp, pnl, equity):
        self.limits.record(timestamp, pnl, equity)
