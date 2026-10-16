import numpy as np
import pandas as pd

from goldsys.ml.dataset import purged_folds
from goldsys.ml.filters import apply_rule_filter, rules_markdown
from goldsys.ml.rule_discovery import discover_rules


def test_planted_rule_is_recovered_and_filter_is_deterministic():
    rng = np.random.default_rng(4)
    x = rng.normal(size=120)
    data = pd.DataFrame({"signal_time": pd.date_range("2020-01-01", periods=120, freq="h", tz="UTC"),
                         "signal_feature": x, "noise": rng.normal(size=120),
                         "label": (x > 0.6).astype(int), "r_multiple": np.where(x > 0.6, 1.0, -1.0)})
    result = discover_rules(data, n_splits=4, embargo=2)
    assert result["accepted"]
    assert result["rules"][0]["feature"] == "signal_feature"
    mask = apply_rule_filter(data, result["rules"])
    assert mask.dtype == bool
    assert "Discovered rules" in rules_markdown(result)


def test_purged_folds_have_embargo_and_noise_is_rejected():
    data = pd.DataFrame({"x": np.arange(30), "label": [0, 1] * 15})
    folds = list(purged_folds(data, n_splits=3, embargo=2))
    for train, test in folds:
        assert not set(train).intersection(test)
        assert all(abs(i - j) > 2 for i in train for j in test)
    result = discover_rules(data, n_splits=3, embargo=2)
    assert not result["accepted"]
