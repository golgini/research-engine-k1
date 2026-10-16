import pandas as pd


class RiskLimits:
    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.daily_loss_cap_pct = float(cfg.get("daily_loss_cap_pct", 0.0))
        self.max_drawdown_pct = float(cfg.get("max_drawdown_pct", 0.0))
        self.max_open_positions = int(cfg.get("max_open_positions", 1))
        self.losing_streak_limit = int(cfg.get("losing_streak_limit", 0))
        self.start_equity = None
        self.peak_equity = None
        self.day = None
        self.day_start = None
        self.day_pnl = 0.0
        self.losing_streak = 0
        self.halted = False

    def can_trade(self, timestamp, equity, open_positions=0):
        if self.halted or open_positions >= self.max_open_positions:
            return False
        self._mark(timestamp, equity)
        if self.daily_loss_cap_pct and self.day_pnl <= -self.day_start * self.daily_loss_cap_pct / 100:
            return False
        if self.max_drawdown_pct and equity <= self.peak_equity * (1 - self.max_drawdown_pct / 100):
            self.halted = True
            return False
        if self.losing_streak_limit and self.losing_streak >= self.losing_streak_limit:
            return False
        return True

    def record(self, timestamp, pnl, equity):
        self._mark(timestamp, equity)
        self.day_pnl += float(pnl)
        self.losing_streak = self.losing_streak + 1 if pnl < 0 else 0

    def _mark(self, timestamp, equity):
        timestamp = pd.Timestamp(timestamp)
        if self.start_equity is None:
            self.start_equity = float(equity)
            self.peak_equity = float(equity)
        self.peak_equity = max(self.peak_equity, float(equity))
        day = timestamp.date()
        if self.day != day:
            self.day = day
            self.day_start = float(equity)
            self.day_pnl = 0.0
