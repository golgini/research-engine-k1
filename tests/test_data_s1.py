import pandas as pd
from goldsys.data.cleaner import clean_bars, flag_gaps
from goldsys.data.loader import detect_timeframe
from goldsys.data.quality import quality_report

def test_detect_timeframe_and_canonical_cleaning(bars):
    assert detect_timeframe(bars) == "H1"
    bad = bars.copy(); bad.iloc[5, bad.columns.get_loc("high")] = bad.iloc[5].open - 2
    cleaned = clean_bars(bad)
    assert cleaned.iloc[5].high >= max(cleaned.iloc[5].open, cleaned.iloc[5].close)

def test_gap_and_quality_report(bars):
    x = bars.drop(bars.index[20:25]); x = flag_gaps(x, max_gap_minutes=60)
    report = quality_report(x)
    assert report["bars"] == len(x)
    assert report["gap_after_count"] >= 1
