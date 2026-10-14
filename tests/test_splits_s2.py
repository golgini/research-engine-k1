import pandas as pd
import pytest
from pathlib import Path
from goldsys.data.splits import get_period, HoldoutLockedError, unlock_holdout

def cfg(tmp_path):
    return {"splits": {"train": ["2020-01-01", "2020-01-03"], "validation": ["2020-01-04", "2020-01-05"], "holdout": ["2020-01-06", "2020-01-07"], "holdout_locked": True, "unlock_flag": str(tmp_path / "unlock")}}

def test_holdout_lock_and_nonoverlapping_periods(tmp_path):
    idx=pd.date_range("2020-01-01", periods=7, freq="D", tz="UTC"); df=pd.DataFrame({"close":range(7)},index=idx)
    c=cfg(tmp_path)
    with pytest.raises(HoldoutLockedError): get_period(df,"holdout",c)
    train, val, dev = get_period(df,"train",c), get_period(df,"validation",c), get_period(df,"dev",c)
    assert train.index.max() < val.index.min(); assert len(dev)==len(train)+len(val)
    unlock_holdout(c, reason="S2 test", user="test"); assert len(get_period(df,"holdout",c)) == 2

def test_load_bars_routes_through_period_lock(tmp_path):
    from goldsys.data.splits import load_bars
    p=tmp_path/"data"/"interim"; p.mkdir(parents=True)
    idx=pd.date_range("2020-01-01", periods=7, freq="D", tz="UTC"); pd.DataFrame({"open":1.,"high":2.,"low":.5,"close":1.,"volume":1.},index=idx).to_parquet(p/"bars_D1.parquet")
    with pytest.raises(HoldoutLockedError): load_bars("D1","holdout",cfg(tmp_path),tmp_path)
