# Build log

## 2026-10-14 — S0–S3 foundation

Created the installable Python package, YAML configuration, canonical CSV loader for the supplied headerless Dukascopy format, cleaning and resampling pipeline, JSON quality report, split manager with a hold-out lock, registered look-ahead-safe core features, strategy signal interface, session-breakout baseline, conservative next-open backtester, and initial performance metrics. Raw source files remain untouched. Known limits: the complete S4–S14 profiling, validation, ML and execution layers remain to be implemented.
## 2026-10-14 — S1 data ingestion and quality

Extended the loader with timeframe detection and canonical schema handling, added OHLC correction flags, intraday gap flags, suspect-bar retention, JSON and Markdown quality reports, and CLI support for automatic timeframe detection. The S1 test suite passes on synthetic data in four tests. The raw 2009–2025 files remain unchanged and excluded from version control; full-dataset materialization is still an operational step to run next.

## 2026-10-14 — S2 split manager and hold-out lock

Added centralized `load_bars`, explicit period validation, train/validation/dev slicing, configurable unlock-flag handling, and timestamped hold-out audit logging with user and reason. The hold-out remains locked unless explicitly unlocked. The full suite passes six tests.

## 2026-10-14 — S3 feature engine

Added registered volatility, session, level, trend, calendar, and structure feature families. Features use rolling/past-only calculations, and confirmed swings are delayed until confirmation bars. Added a prefix-versus-full-series look-ahead regression test. The full suite passes eight tests.

## 2026-10-15 — S4 market profiler

Added development-period-only profiling for returns by hour, weekday, month, and session; volatility clustering; Asian-range breakout behavior; large-move follow-through; candidate hypothesis ranking; and HTML/JSON outputs. The profiler routes through the split manager and never requests the locked hold-out. The full suite passes nine tests.

## 2026-10-15 — S5 regime detection

Added rolling-only rule-based regimes using ADX, EMA slope, and ATR percentile. Combined trend/volatility labels are registered as features, yearly regime statistics are exportable, and the `goldsys regimes run` CLI writes CSV output. Added prefix-versus-full-series look-ahead coverage for regime labels.

## 2026-10-15 — S6 backtest engine

Added cost and broker simulation modules with adverse spread/slippage, commission, swap, market-next-open, stop, and limit handling; gap-aware stops; pending-order expiry; configurable SL/TP conflict; MAE/MFE; time stops; mark-to-market equity; and the standard trade ledger. The full suite passes fourteen tests.

## 2026-10-15 — S7 strategy library

Added trend-momentum, mean-reversion, and liquidity-sweep reversal baselines; registered all four strategies; exposed parameter spaces; documented each strategy thesis; and added synthetic geometry tests. The full suite passes seventeen tests.

## 2026-10-15 — S8 metrics and reporting

Expanded performance metrics with risk-adjusted returns, drawdown, exposure, trade-quality, streak, MAE/MFE, ulcer, and monthly-return statistics. Added JSON/HTML backtest reports, trade CSV output, and the goldsys backtest run CLI. The report layer is covered by hand-computed synthetic metrics tests.

## 2026-10-15 — S9 validation suite

Added configurable validation gates, seeded Monte Carlo trade stress, parameter sensitivity evaluation, cost stress, walk-forward evaluation, and the goldsys validate run CLI. Validation is scoped to the development period and does not request the locked holdout. The full suite passes twenty-three tests.

## 2026-10-15 — S10 ML rule discovery

Added a dependency-light signal dataset builder, purged and embargoed folds, shallow threshold-rule discovery with cross-validated AUC and stability gates, deterministic rule filters, Markdown rule reports, and the goldsys ml discover CLI. The full suite passes twenty-five tests.

## 2026-10-15 — S11 risk and portfolio layer

Added fixed-fractional sizing with lot rounding and minimum-lot rejection, daily loss and drawdown kill switches, open-position and losing-streak limits, a backtester sizing hook, and multi-strategy equity/correlation combination. The full suite passes twenty-eight tests.

## 2026-10-15 — S12 final holdout framework

Added reproducible candidate freezing with configuration hashes and a one-shot final-test path that routes through the existing holdout lock. The CLI requires explicit confirmation for the final holdout command; no holdout data is accessed by default.

## 2026-10-16 — S13 execution layer

Added paper replay using the same signal and broker path as backtests, trade-log and daily-summary output, MT5 EA specification/MQL5 skeleton exports, Pine Script alert exports, and an opt-in disabled-by-default Telegram boundary. No live order transport is implemented.
