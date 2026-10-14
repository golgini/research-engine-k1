from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal
import pandas as pd

@dataclass
class Signal:
    time: pd.Timestamp
    side: Literal["long", "short"]
    entry_type: Literal["market_next_open", "stop", "limit"]
    entry_price: float | None
    stop_loss: float
    take_profit: float | None
    expiry_bars: int | None
    meta: dict = field(default_factory=dict)

class Strategy(ABC):
    name = "base"
    def __init__(self, params=None): self.params = params or {}
    def required_features(self): return ["atr_14"]
    @abstractmethod
    def generate_signals(self, bars, feats): ...
    def param_space(self): return {}
