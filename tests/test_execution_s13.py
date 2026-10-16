from goldsys.execution.mt5_spec import export_mt5
from goldsys.execution.paper_runner import replay_paper, write_paper_log
from goldsys.execution.pine_export import export_pine
from goldsys.execution.telegram_bot import ENABLED


def test_exports_and_paper_runner_parity(bars, tmp_path):
    cfg = {"engine": {"initial_equity": 1000}, "costs": {"point_value_per_lot": 1}}
    result = replay_paper(bars, "trend_momentum", cfg)
    assert list(result.trades.columns)
    summary = write_paper_log(result, tmp_path / "paper")
    assert summary["trades"] == len(result.trades)
    assert (tmp_path / "paper" / "trade_log.csv").exists()
    assert export_mt5("trend_momentum", {"rr": 2}, tmp_path / "export").joinpath("EA_SPEC.md").exists()
    assert export_pine("trend_momentum", tmp_path / "export").exists()
    assert ENABLED is False
