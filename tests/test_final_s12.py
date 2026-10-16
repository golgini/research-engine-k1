import pandas as pd
import pytest

from goldsys.data.splits import HoldoutLockedError
from goldsys.validation.final_test import freeze_candidate, run_final_test


def test_freeze_candidate_is_hashed_and_reproducible(tmp_path):
    cfg = {"project": {"seed": 42}, "splits": {"holdout_locked": True}}
    first, digest_a = freeze_candidate("trend_momentum", {"rr": 2.0}, cfg, tmp_path)
    second, digest_b = freeze_candidate("trend_momentum", {"rr": 2.0}, cfg, tmp_path)
    assert first == second
    assert digest_a == digest_b
    assert len(digest_a) == 64
    assert "config_hash:" in first.read_text()


def test_final_test_respects_holdout_lock(bars, tmp_path):
    cfg = {"splits": {"train": ["2020-01-01", "2020-01-05"],
                      "validation": ["2020-01-06", "2020-01-10"],
                      "holdout": ["2020-01-11", "2020-01-12"],
                      "holdout_locked": True, "unlock_flag": str(tmp_path / "unlock")}}
    with pytest.raises(HoldoutLockedError):
        run_final_test(bars, "trend_momentum", cfg, {"rr": 2.0})
