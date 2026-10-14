import numpy as np
import pandas as pd
import pytest
@pytest.fixture
def bars():
    idx=pd.date_range("2020-01-01", periods=400, freq="h", tz="UTC")
    close=1800+np.cumsum(np.random.default_rng(42).normal(0,1,len(idx)))
    return pd.DataFrame({"open":close,"high":close+1,"low":close-1,"close":close,"volume":100.},index=idx).rename_axis("time")
