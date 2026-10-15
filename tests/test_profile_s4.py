import pandas as pd
from goldsys.profiling.profiler import profile_market, run_profile

def test_profile_has_required_studies(bars, tmp_path):
    cfg={"splits":{"train":["2020-01-01","2020-01-05"],"validation":["2020-01-06","2020-01-10"],"holdout":["2020-01-11","2020-01-12"],"holdout_locked":True,"unlock_flag":str(tmp_path/"unlock")}}
    result=profile_market(bars,cfg)
    assert {"returns_by_hour","returns_by_session","asian_breakout","big_move_study"} <= result.keys()
    run_profile(bars,cfg,tmp_path/"profile",tmp_path/"hypotheses.md")
    assert (tmp_path/"profile"/"profile.html").exists()
