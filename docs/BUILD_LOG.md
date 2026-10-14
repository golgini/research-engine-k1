# Build log

## 2026-10-14 — S0–S3 foundation

Created the installable Python package, YAML configuration, canonical CSV loader for the supplied headerless Dukascopy format, cleaning and resampling pipeline, JSON quality report, split manager with a hold-out lock, registered look-ahead-safe core features, strategy signal interface, session-breakout baseline, conservative next-open backtester, and initial performance metrics. Raw source files remain untouched. Known limits: the complete S4–S14 profiling, validation, ML and execution layers remain to be implemented.
## 2026-10-14 — S1 data ingestion and quality

Extended the loader with timeframe detection and canonical schema handling, added OHLC correction flags, intraday gap flags, suspect-bar retention, JSON and Markdown quality reports, and CLI support for automatic timeframe detection. The S1 test suite passes on synthetic data in four tests. The raw 2009–2025 files remain unchanged and excluded from version control; full-dataset materialization is still an operational step to run next.

## 2026-10-14 — S2 split manager and hold-out lock

Added centralized `load_bars`, explicit period validation, train/validation/dev slicing, configurable unlock-flag handling, and timestamped hold-out audit logging with user and reason. The hold-out remains locked unless explicitly unlocked. The full suite passes six tests.

## 2026-10-14 — S3 feature engine

Added registered volatility, session, level, trend, calendar, and structure feature families. Features use rolling/past-only calculations, and confirmed swings are delayed until confirmation bars. Added a prefix-versus-full-series look-ahead regression test. The full suite passes eight tests.
