import pandas as pd
from goldsys.features.base import build_features

def test_registered_feature_families(bars):
    f=build_features(bars,{})
    expected={"atr_14","session_high_so_far","prev_day_high","adx_14","hour","confirmed_swing_high"}
    assert expected <= set(f.columns)

def test_features_do_not_change_when_future_is_appended(bars):
    cut=250; prefix=build_features(bars.iloc[:cut],{}); full=build_features(bars,{})
    cols=[c for c in prefix.columns if c in full.columns]
    pd.testing.assert_frame_equal(prefix[cols].iloc[-1:],full[cols].iloc[cut-1:cut],check_dtype=False,check_names=False)
