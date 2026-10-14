# GOLDSYS

Look-ahead-safe XAUUSD research and backtesting foundation based on `GOLD SYSTEM BUILD SPEC.md`.

## Quick start

    python -m pip install -e .
    goldsys data ingest --timeframe H1
    goldsys data quality --timeframe H1
    goldsys features --timeframe H1
    goldsys strategies

The supplied files are Dukascopy-style, headerless XAUUSD CSVs with date, time, OHLC and volume columns. Raw files remain untouched. Cleaned bars are written to `data/interim`; features go to `data/processed`; quality output goes to `reports`.

The 2023–2025 hold-out is locked by default. Unlocking requires an explicit `goldsys holdout unlock --confirm` command and is logged.

This is research software, not a live-money trading system. Any strategy must survive costs, walk-forward validation and paper trading before capital is considered.
