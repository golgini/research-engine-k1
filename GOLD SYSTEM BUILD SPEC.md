# GOLD (XAUUSD) RESEARCH & STRATEGY SYSTEM: FULL BUILD SPEC

**Audience:** Codex (or any coding agent). Build this system from zero to finished product by executing the sessions in Section 7 in order.
**Data:** Gold CSV data, 2009 to 2025 (timeframe may be M1, M5, M15, H1 or D1; the system must auto-detect and be configurable).
**Language:** Python 3.11+.

---

## 0. RULES OF ENGAGEMENT (READ FIRST)

1. Execute sessions strictly in order (S0, S1, S2, ...). Never start a session until the previous session's **Acceptance Criteria** pass.
2. Each session only creates or edits the files listed under its **Files** heading. Never restructure earlier modules. If an earlier module needs a change, add an extension point; do not rewrite it.
3. All interfaces in Section 6 are **frozen**. Implement them exactly. Later sessions depend on them.
4. Every session ends with: tests passing (`pytest -q`), a short entry appended to `docs/BUILD_LOG.md` (what was built, decisions, known limits), and a git commit `S<n>: <title>`.
5. No look-ahead, ever. See Section 8. Tests enforce this.
6. Never read, plot or tune on the **hold-out period** before Session S12. The data layer must enforce this in code (Section 7, S2).
7. Everything is config-driven (`config/config.yaml`). No magic numbers in code.
8. Deterministic: fixed random seeds from config; same input gives same output.
9. If something is ambiguous, choose the simplest conservative option, document it in `docs/BUILD_LOG.md`, and continue. Do not stop to ask.
10. Do not add features that are not in this spec until S14 is complete.

---

## 1. GOAL

Build a research pipeline that:
1. Ingests and validates 2009-2025 gold data.
2. Profiles how gold actually behaves (sessions, volatility, events, regimes).
3. Provides a library of rule-based strategies built on testable hypotheses.
4. Backtests them with realistic costs and conservative fill logic.
5. Validates them with walk-forward, sensitivity, Monte Carlo, cost stress and regime analysis.
6. Uses ML only as a **rule-discovery and filtering aid**, not as a price predictor.
7. Applies a risk engine, passes a one-time hold-out test, and exports the winning rules for execution (MT5 EA spec, Pine Script, paper-trade runner, optional Telegram signals).

**Non-goals:** predicting price directly with deep learning, high-frequency/tick strategies, live money execution (only paper/demo execution is in scope).

---

## 2. DESIGN PRINCIPLES

- Hypothesis first, data second. Every strategy has a written thesis (`docs/hypotheses.md`).
- Robust over optimal: prefer parameter plateaus to sharp peaks.
- Costs are first-class: spread, slippage, commission, swap.
- Conservative fills: if SL and TP are both touched in one bar, assume **SL hit first**.
- Signals are computed on **closed bars**; orders fill at the **next bar open** (plus costs).
- Separation of concerns: data / features / strategies / engine / validation / risk / reporting / execution are independent packages.

---

## 3. TECH STACK

- Python 3.11+, `pandas`, `numpy`, `pyarrow` (parquet), `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`, `pyyaml`, `pydantic` (config validation), `typer` (CLI), `pytest`, `jinja2` (reports), `hmmlearn` (optional regime model), `numba` (optional speedups), `python-telegram-bot` (optional, S13).
- Packaging: `pyproject.toml`, editable install (`pip install -e .`).
- Lint/format: `ruff`, `black`. Type hints on all public functions.

---

## 4. REPOSITORY STRUCTURE (CREATE IN S0)

```
gold-system/
├── pyproject.toml
├── README.md
├── Makefile
├── config/
│   ├── config.yaml
│   └── strategies/              # one yaml per strategy param set
├── data/
│   ├── raw/                     # user drops CSVs here (never modified)
│   ├── interim/                 # cleaned parquet
│   └── processed/               # feature parquet, resampled bars
├── docs/
│   ├── BUILD_LOG.md
│   ├── hypotheses.md
│   ├── ARCHITECTURE.md
│   └── DATA_DICTIONARY.md
├── src/goldsys/
│   ├── __init__.py
│   ├── config.py                # pydantic config loader
│   ├── logging_setup.py
│   ├── data/
│   │   ├── loader.py            # CSV ingestion + schema detection
│   │   ├── cleaner.py           # dedupe, gaps, bad ticks, tz
│   │   ├── resampler.py         # timeframe conversion
│   │   ├── quality.py           # data quality report
│   │   └── splits.py            # train/val/holdout manager + lock
│   ├── features/
│   │   ├── base.py              # feature registry
│   │   ├── volatility.py        # ATR, realized vol, percentiles
│   │   ├── sessions.py          # Asia/London/NY labels + ranges
│   │   ├── structure.py         # swings, HH/HL, SNR zones, sweeps, FVG
│   │   ├── trend.py             # MAs, ADX, momentum, slope
│   │   ├── levels.py            # prev day/week hi/lo, VWAP, round numbers
│   │   └── calendar.py          # weekday, month, hour, event flags
│   ├── profiling/
│   │   ├── profiler.py          # session/hour/weekday/month stats
│   │   ├── events.py            # event studies
│   │   └── report.py
│   ├── regimes/
│   │   ├── rules.py             # ADX/ATR rule-based regimes
│   │   └── hmm.py               # optional HMM regimes
│   ├── strategies/
│   │   ├── base.py              # Strategy ABC (frozen interface)
│   │   ├── registry.py
│   │   ├── session_breakout.py
│   │   ├── trend_momentum.py
│   │   ├── mean_reversion.py
│   │   └── liquidity_sweep.py
│   ├── engine/
│   │   ├── costs.py             # spread/slippage/commission/swap
│   │   ├── broker_sim.py        # fills, SL/TP, intrabar rules
│   │   ├── backtester.py        # main loop
│   │   └── portfolio.py         # equity curve, trade ledger
│   ├── metrics/
│   │   ├── performance.py
│   │   └── trade_stats.py
│   ├── validation/
│   │   ├── walk_forward.py
│   │   ├── sensitivity.py
│   │   ├── monte_carlo.py
│   │   ├── cost_stress.py
│   │   ├── regime_breakdown.py
│   │   └── gate.py              # pass/fail criteria
│   ├── ml/
│   │   ├── dataset.py           # labels + features, purged CV
│   │   ├── rule_discovery.py    # shallow trees, importance
│   │   └── filters.py           # ML trade filter wrapper
│   ├── risk/
│   │   ├── sizing.py
│   │   ├── limits.py            # daily loss cap, max DD kill switch
│   │   └── engine.py
│   ├── reporting/
│   │   ├── plots.py
│   │   ├── html_report.py
│   │   └── templates/
│   ├── execution/
│   │   ├── mt5_spec.py          # generates EA spec markdown/MQL5 skeleton
│   │   ├── pine_export.py
│   │   ├── paper_runner.py
│   │   └── telegram_bot.py      # optional
│   └── cli.py                   # typer entrypoint: `goldsys ...`
├── tests/
│   ├── conftest.py              # synthetic data fixtures
│   ├── test_data_*.py
│   ├── test_features_*.py
│   ├── test_no_lookahead.py
│   ├── test_engine_*.py
│   ├── test_validation_*.py
│   └── test_holdout_lock.py
├── notebooks/                   # optional exploration (never imported by src)
└── reports/                     # generated outputs (gitignored except .gitkeep)
```

---

## 5. CONFIG (`config/config.yaml`), CREATE IN S0

```yaml
project:
  seed: 42
  symbol: XAUUSD

data:
  raw_dir: data/raw
  file_glob: "*.csv"
  datetime_column: auto          # auto-detect; or explicit name
  datetime_format: auto
  timezone_source: UTC           # timezone of raw timestamps; CHANGE if known otherwise
  timezone_market: UTC
  base_timeframe: auto           # auto-detect from median bar spacing
  analysis_timeframes: [M15, H1, H4, D1]
  price_decimals: 2
  max_gap_minutes_intraday: 60   # gaps beyond this (outside weekends) are flagged
  bad_tick_atr_multiple: 15      # bar range > N * ATR flagged as suspect

splits:
  train: ["2009-01-01", "2019-12-31"]
  validation: ["2020-01-01", "2022-12-31"]
  holdout: ["2023-01-01", "2025-12-31"]
  holdout_locked: true           # set false ONLY in S12 via CLI flag

sessions_utc:                    # editable; used for session features
  asia:   ["00:00", "07:00"]
  london: ["07:00", "12:00"]
  ny:     ["12:00", "21:00"]

costs:
  spread_points: 0.30            # XAUUSD price units (USD). Typical 0.20-0.50
  spread_widening_news: 2.0      # multiplier near news windows
  slippage_points: 0.10
  commission_per_lot: 0.0        # round-turn USD, broker dependent
  swap_long_per_lot_per_day: -0.0
  swap_short_per_lot_per_day: -0.0
  contract_size: 100             # oz per 1.0 lot
  point_value_per_lot: 100       # USD per 1.00 price move per 1.0 lot

engine:
  initial_equity: 10000
  fill_model: next_open
  intrabar_conflict: sl_first    # conservative
  allow_multiple_positions: false
  max_bars_in_trade: null

risk:
  risk_per_trade_pct: 0.5
  max_daily_loss_pct: 2.0
  max_drawdown_kill_pct: 15.0
  max_open_positions: 1
  min_lot: 0.01
  lot_step: 0.01
  max_lot: 5.0

validation:
  walk_forward:
    train_years: 3
    test_years: 1
    step_years: 1
  monte_carlo_runs: 2000
  sensitivity_grid_pct: [-30, -15, 0, 15, 30]
  cost_stress_multipliers: [1.0, 1.5, 2.0, 3.0]
  gate:
    min_trades: 150
    min_profit_factor: 1.25
    min_expectancy_r: 0.10
    max_drawdown_pct: 25
    min_positive_wf_windows_pct: 60
    max_pf_degradation_oos_vs_is_pct: 35
    min_pf_at_2x_costs: 1.05

ml:
  model: decision_tree             # decision_tree | random_forest | gradient_boosting
  max_depth: 4
  min_samples_leaf: 100
  cv_scheme: purged_kfold
  cv_folds: 5
  embargo_bars: 24
```

---

## 6. FROZEN INTERFACES

### 6.1 Canonical bar DataFrame
Index: `DatetimeIndex` (tz-aware, UTC), name `time`, sorted ascending, unique.
Columns (lowercase, float64 unless noted): `open, high, low, close, volume` (volume may be NaN or tick volume), plus optional `spread`.
Everything downstream uses this schema.

### 6.2 Feature function
```python
FeatureFn = Callable[[pd.DataFrame, dict], pd.DataFrame]
# input: canonical bars + params dict
# output: DataFrame aligned to input index, new columns only, NaN-safe, NO look-ahead
```
Registered via `@register_feature("name")` in `features/base.py`. `build_features(bars, cfg) -> DataFrame` merges all registered features.

### 6.3 Strategy ABC (`strategies/base.py`)
```python
@dataclass
class Signal:
    time: pd.Timestamp        # time of the CLOSED bar that generated it
    side: Literal["long", "short"]
    entry_type: Literal["market_next_open", "stop", "limit"]
    entry_price: float | None # for stop/limit
    stop_loss: float          # absolute price
    take_profit: float | None # absolute price (None => use exit rule)
    expiry_bars: int | None   # pending order validity
    meta: dict                # tags: strategy, setup, regime, etc.

class Strategy(ABC):
    name: str
    params: dict
    def required_features(self) -> list[str]: ...
    def generate_signals(self, bars: pd.DataFrame, feats: pd.DataFrame) -> list[Signal]: ...
    def param_space(self) -> dict[str, list]: ...   # for sensitivity / walk-forward
```
Signals must be computable using data up to and including the signal bar only.

### 6.4 Trade ledger (`engine/portfolio.py`)
Columns: `trade_id, strategy, side, signal_time, entry_time, entry_price, exit_time, exit_price, exit_reason (sl|tp|time|eod|kill), lots, sl_price, tp_price, risk_amount, gross_pnl, costs, net_pnl, r_multiple, mae, mfe, bars_held, meta(json)`.

### 6.5 Backtest result
```python
@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.Series          # indexed by bar time
    config_snapshot: dict
    strategy: str
    params: dict
    period: tuple[str, str]
```

### 6.6 Split manager (`data/splits.py`)
```python
get_period(df, name: Literal["train","validation","holdout","dev"]) -> DataFrame
# "dev" = train + validation
# Requesting "holdout" while holdout_locked is true raises HoldoutLockedError.
```

---

## 7. SESSIONS (BUILD ORDER)

Each session: **Objective / Files / Tasks / Acceptance / Do-not**.

### S0: Project scaffold
**Objective:** Empty but runnable project.
**Files:** `pyproject.toml`, `README.md`, `Makefile`, `config/config.yaml`, `src/goldsys/{__init__,config,logging_setup,cli}.py`, `docs/*`, `tests/conftest.py`, full directory tree from Section 4 with `__init__.py` files.
**Tasks:**
- Create the repo tree. Implement `config.py` (pydantic models mirroring Section 5, `load_config(path)`).
- `logging_setup.py`: console + file logging to `reports/logs/`.
- `cli.py`: Typer app with `goldsys --help` and a `goldsys version` command.
- `conftest.py`: synthetic OHLCV generator (random walk with sessions, gaps, weekends) used by all tests. Provide fixtures for M15, H1, D1.
- Makefile targets: `install`, `test`, `lint`, `format`.
**Acceptance:** `pip install -e .`, `goldsys version` works, `pytest -q` passes, config loads and validates.
**Do-not:** write any trading logic.

### S1: Data ingestion, cleaning, quality
**Objective:** Turn any reasonable gold CSV into canonical bars + a quality report.
**Files:** `data/loader.py`, `cleaner.py`, `resampler.py`, `quality.py`, `docs/DATA_DICTIONARY.md`, tests.
**Tasks:**
- `loader`: read all CSVs in `data/raw`, auto-detect delimiter, header, datetime column(s) (single column, or separate date+time columns), column name variants (`Open/O`, `Vol/Volume/Tick Volume`, etc.), datetime format. Concatenate, sort, localize to `timezone_source`, convert to UTC.
- `cleaner`: drop exact duplicate rows; for duplicate timestamps keep last; remove rows with non-positive prices; enforce `low <= open,close <= high` (fix or flag); flag (do not delete) suspect bars (range > `bad_tick_atr_multiple` x rolling ATR); flag gaps beyond threshold excluding weekends; output `is_suspect` boolean column kept in interim data.
- `resampler`: resample to any timeframe (M1..D1, W1) with correct OHLC aggregation, bar label = bar open time, drop incomplete weekend bars.
- `quality`: JSON + markdown report: date range, bar count, detected timeframe, missing bars by year, gap list, suspect-bar count, bars per year, volume availability, price range sanity (gold 2009 ~ $800-1200, 2025 > $2000; flag anomalies).
- Save cleaned base bars to `data/interim/bars_<tf>.parquet`; resampled to `data/processed/`.
- CLI: `goldsys data ingest`, `goldsys data quality`.
**Acceptance:** On synthetic data and on a real CSV the pipeline produces parquet in canonical schema, quality report generated, no duplicate or unsorted index, tests cover multiple CSV formats.
**Do-not:** touch splits or compute features.

### S2: Split manager and hold-out lock
**Objective:** Enforce the research discipline in code.
**Files:** `data/splits.py`, `tests/test_holdout_lock.py`.
**Tasks:**
- Implement `get_period` per 6.6. Holdout access when locked raises `HoldoutLockedError` (a custom exception) with a clear message.
- Unlock only via CLI `goldsys holdout unlock --confirm` which writes `reports/holdout_access.log` (timestamp, user, reason) and flips an on-disk flag file `config/.holdout_unlocked`. Config `holdout_locked` AND absence of the flag file means locked.
- Every function in later sessions that loads data must go through `get_period`. Provide `load_bars(timeframe, period)` helper.
- Add a test that scans `src/` for direct parquet reads of data files outside `data/` package and fails if found.
**Acceptance:** Requesting holdout raises; train/validation/dev return correct date slices with no overlap; test scan passes.

### S3: Feature engine
**Objective:** Reusable, look-ahead-safe features.
**Files:** `features/*.py`, `tests/test_features_*.py`, `tests/test_no_lookahead.py`.
**Tasks (registered features):**
- `volatility`: ATR(n), true range, realized vol, ATR percentile (rolling), range/ATR ratio.
- `sessions`: session label per bar (asia/london/ny/off), session open/high/low so far, previous-session high/low, Asian range size, bars since session open.
- `levels`: previous day/week/month high-low-close, current day open, rolling VWAP (if volume available else typical-price average), distance to levels in ATR units, nearest round number (multiples of 10/50/100).
- `trend`: EMA/SMA set, slope, ADX, momentum (ROC), higher-timeframe trend flag (merged from resampled HTF using only completed HTF bars).
- `structure`: swing highs/lows (fractal, `left/right` params; swing is confirmed only `right` bars later, so the feature is timestamped at confirmation time), HH/HL/LH/LL state, break-of-structure flag, liquidity sweep (wick beyond prior swing/session extreme then close back inside), engulfing pattern, fair value gap (3-candle gap, recorded at candle 3 close), simple SNR zones (clustered swing levels, updated only with confirmed swings).
- `calendar`: hour, weekday, month, day-of-month, first-trading-day flags, optional `events.csv` loader (user-provided NFP/FOMC/CPI dates; if absent, skip gracefully).
- `build_features(bars, cfg)` merges all and caches to `data/processed/features_<tf>.parquet`.
**Look-ahead test (mandatory):** For N random cut points `t`, compute features on `bars[:t]` and on full `bars`; values at `t-1` must be identical. Fail the build otherwise.
**Acceptance:** All features computed on synthetic + real data; look-ahead test passes; NaNs only in warm-up periods.
**Do-not:** use `shift(-n)`, centered rolling windows, or full-sample statistics (e.g. global percentile).

### S4: Market profiler
**Objective:** Describe how gold behaves, producing hypothesis candidates.
**Files:** `profiling/{profiler,events,report}.py`, tests.
**Scope of data:** `dev` period only (train + validation).
**Tasks:**
- Returns/volatility by hour-of-day, session, weekday, month, year; hit-rate (up bars %), mean return, std, t-stat, with multiple-testing note (Bonferroni or FDR flag).
- Volatility clustering: autocorrelation of |returns| and ATR; GARCH(1,1) fit summary on daily returns.
- Asian-range breakout study: how often London breaks Asian high vs low first; follow-through distribution (in ATR units); fake-out rate.
- Sweep study: after a previous-day-high/low sweep, distribution of next N-bar forward returns.
- Event study around big-move bars (>2 ATR): forward return distributions (continuation vs reversal).
- Trend persistence: Hurst exponent / variance ratio by year.
- Round-number reaction study.
- Output: `reports/profile/profile.html` + `profile_summary.json` + a ranked "candidate hypotheses" table (effect size, t-stat, sample size) written to `docs/hypotheses.md` (append, never overwrite).
- CLI: `goldsys profile run`.
**Acceptance:** Report generates on dev data; contains all studies; no holdout access (test asserts).

### S5: Regime detection
**Objective:** Label every bar with a regime for conditional analysis.
**Files:** `regimes/{rules,hmm}.py`, tests.
**Tasks:**
- Rule-based regimes: trend vs range (ADX + MA slope), volatility high/normal/low (ATR percentile, rolling window only). Combined label e.g. `trend_highvol`.
- Optional HMM (2-3 states on returns + volatility) fit on **train only**, applied forward to validation with no refit. Persist model.
- Output a `regime` column merged into features; regime stats table (share of time, avg return, avg vol by year).
**Acceptance:** Regimes have no look-ahead (rolling only); stats table generated; HMM fit uses train data only (test asserts).

### S6: Backtest engine
**Objective:** Realistic, conservative simulator.
**Files:** `engine/{costs,broker_sim,backtester,portfolio}.py`, `tests/test_engine_*.py`.
**Tasks:**
- `costs`: spread (static + widening near events/rollover hour if configured), slippage, commission, swap by days held. Entry cost applied adversely; exits likewise.
- `broker_sim`: process signals into orders. `market_next_open` fills at next bar open +/- costs. `stop`/`limit` orders fill when bar range touches price (stops with slippage; limits without improvement unless open gaps through). SL/TP checked each bar after entry; if both inside a single bar, apply `intrabar_conflict` (default SL first). Gap handling: if open gaps beyond SL, fill at open (worse price). Pending order expiry. Track MAE/MFE.
- `backtester`: loop over bars, no overlapping positions if `allow_multiple_positions` is false, apply risk-engine sizing hook (stubbed with fixed 1% risk until S11), kill-switch hook.
- `portfolio`: equity curve (mark-to-market per bar), trade ledger per 6.4, R-multiples.
- Deterministic and vectorised where safe; add `numba` only if needed.
**Tests:** hand-built bar sequences verifying: SL-first conflict, gap-through-stop fill, spread cost on both sides, swap accrual, R-multiple calc, no trade on last bar, no fill using same-bar close.
**Acceptance:** All engine tests pass; a trivial always-long strategy on synthetic drift data produces expected PnL within tolerance.

### S7: Strategy library
**Objective:** Implement the strategy ABC and four baseline strategies, each with a written thesis in `docs/hypotheses.md`.
**Files:** `strategies/{base,registry,session_breakout,trend_momentum,mean_reversion,liquidity_sweep}.py`, `config/strategies/*.yaml`, tests.
**Strategies:**
1. **Session breakout:** trade breakout of the Asian range during London/NY open; SL at opposite side or ATR-based; TP at R multiple; optional trend/regime filter; one trade per day.
2. **Trend momentum:** trade pullbacks or breakouts in the direction of HTF trend (EMA alignment + ADX threshold); ATR trailing stop exit.
3. **Mean reversion:** fade extensions beyond N ATR from VWAP/MA in ranging regime; time-stop and hard SL.
4. **Liquidity sweep reversal:** sweep of previous-day/session extreme + engulfing/BOS confirmation in kill-zone hours; SL beyond sweep wick, TP at R multiple or opposite level. (Codify the user's SNR/liquidity-sweep ideas as exact rules.)
- Every strategy exposes `param_space()` with sane ranges and defaults in yaml.
- `registry`: `get_strategy(name, params)`; `goldsys strategies list`.
**Acceptance:** Each strategy generates signals on synthetic data with valid SL/TP geometry (SL on the correct side), signals only use data up to signal bar (extend look-ahead test to strategies), CLI lists them.

### S8: Metrics and reporting
**Objective:** Standardised evaluation and human-readable output.
**Files:** `metrics/{performance,trade_stats}.py`, `reporting/{plots,html_report}.py`, templates, tests.
**Metrics:** net profit, CAGR, annualised return/vol, Sharpe, Sortino, Calmar, max drawdown (% and duration), profit factor, win rate, avg win/loss, payoff, expectancy (R), trades/year, exposure %, longest losing streak, best/worst trade, MAE/MFE stats, monthly returns table, rolling Sharpe, ulcer index.
**Plots:** equity curve + drawdown, monthly heatmap, R-multiple histogram, PnL by hour/weekday/session/regime, trade scatter (MAE vs MFE).
**Report:** `goldsys backtest run --strategy X --period dev` writes `reports/backtests/<strategy>_<timestamp>/report.html`, `trades.csv`, `metrics.json`.
**Acceptance:** Metrics verified against hand-computed values in tests; report renders from a synthetic backtest.

### S9: Validation suite
**Objective:** Decide whether an edge is real.
**Files:** `validation/*.py`, tests.
**Tasks:**
- `walk_forward`: rolling windows per config (optimise on train window by a chosen objective with a minimum-trade constraint, then test on next window with chosen params; stitch OOS equity). Output IS vs OOS metrics per window and degradation %.
- `sensitivity`: vary each param across `sensitivity_grid_pct`; heatmaps for 2-param pairs; compute a "plateau score" (share of neighbouring cells with PF above threshold).
- `monte_carlo`: (a) shuffle trade order, (b) bootstrap trades with replacement, (c) randomly skip 10% of trades; report distribution of max DD, final equity, probability of ruin / of exceeding the DD limit.
- `cost_stress`: rerun with spread/slippage multipliers; report break-even cost multiple.
- `regime_breakdown`: metrics per regime and per year.
- `gate`: apply thresholds from config; emit PASS/FAIL per criterion and overall verdict; write `reports/validation/<strategy>/gate.json`.
- CLI: `goldsys validate run --strategy X`.
**Scope:** `dev` period only.
**Acceptance:** Suite runs end-to-end on a synthetic strategy; gate returns correct PASS/FAIL on constructed cases (a known-good synthetic edge passes; pure noise fails).

### S10: ML rule discovery (optional filter layer)
**Objective:** Learn which conditions separate winning from losing setups; output human-readable rules.
**Files:** `ml/{dataset,rule_discovery,filters}.py`, tests.
**Tasks:**
- `dataset`: for each historical signal from a strategy, build a row: features at signal time (no look-ahead) + label (win = R > 0, or R-bucket). Purged k-fold CV with embargo (config).
- `rule_discovery`: shallow decision tree (depth <= `max_depth`), feature importances, permutation importance, export tree as plain-text if/else rules. Compare model AUC to baseline; **reject if CV AUC < 0.55 or unstable across folds.**
- `filters`: wrapper that turns accepted rules into a deterministic filter applied inside the strategy (rules hand-coded into config, not a live model call), then re-run S9 validation with the filter.
- Report: `reports/ml/<strategy>/rules.md`.
**Acceptance:** On a synthetic dataset with a planted rule the tree recovers it; on noise it is rejected by the AUC gate; no train/test leakage (test asserts purging).

### S11: Risk engine and portfolio layer
**Objective:** Capital-preserving sizing and limits.
**Files:** `risk/{sizing,limits,engine}.py`, tests; update backtester to use it via the existing hook (extension, not rewrite).
**Tasks:**
- Sizing: fixed fractional risk (lots from risk amount / SL distance x point value), rounded to `lot_step`, clamped to `min/max_lot`; reject trades whose min-lot risk exceeds 2x target.
- Limits: daily loss cap (stop trading rest of day), max drawdown kill switch (flatten and halt until manual reset), max open positions, optional losing-streak cooldown.
- Optional volatility-targeted sizing.
- Multi-strategy portfolio runner: run several strategies, combine equity, shared risk limits, correlation matrix of strategy returns.
**Acceptance:** Sizing math tests; limits trigger correctly in constructed sequences; portfolio of two strategies yields combined equity and correlation output.

### S12: Final hold-out test and selection
**Objective:** One-shot unbiased evaluation.
**Files:** `validation/final_test.py`, CLI additions, `reports/final/`.
**Tasks:**
- Shortlist = strategies (with frozen params and any ML-derived filters) that passed the S9 gate on dev data. Freeze params in `config/frozen/<strategy>.yaml` with hash.
- `goldsys holdout unlock --confirm`, run each frozen strategy once on 2023-2025, compute same metrics, compare with dev results.
- Pass criteria: PF >= 1.1, expectancy > 0, drawdown within the gate limit, and PF degradation vs dev no worse than the configured limit. If a strategy fails, record it and do **not** re-tune and re-test on the same hold-out.
- Output `reports/final/final_report.html` (+ JSON) with a verdict per strategy.
**Acceptance:** Report generated; access logged; re-running without a new unlock is blocked; verdicts reproducible.

### S13: Execution layer (paper first)
**Objective:** Turn approved rules into something runnable.
**Files:** `execution/{mt5_spec,pine_export,paper_runner,telegram_bot}.py`, docs.
**Tasks:**
- `mt5_spec`: generate `reports/export/<strategy>/EA_SPEC.md` (inputs, entry/exit rules, risk, filters, session times in broker time, test cases) and an MQL5 skeleton `.mq5` with the rule logic as commented pseudocode and parameter inputs.
- `pine_export`: generate a Pine Script v5 strategy/indicator reproducing the signals with alerts.
- `paper_runner`: replays or polls bars (CSV feed adapter interface), runs the strategy + risk engine, writes a live-style trade log and daily summary; same code path as the backtester for signal generation.
- `telegram_bot` (optional, off by default): posts signals/daily summaries; token via env var, never in config.
- Parity test: paper runner over historical dev data reproduces backtester trades (same signals and entries).
**Acceptance:** Export files generated for an approved strategy; parity test passes; bot module imports without a token and is disabled by default.

### S14: CLI polish, docs, final QA
**Objective:** Finished, documented product.
**Files:** `cli.py`, `README.md`, `docs/ARCHITECTURE.md`, `docs/BUILD_LOG.md`, CI config (optional).
**Tasks:**
- One-command pipeline: `goldsys pipeline run --through validate` executing S1 to S9 for configured strategies.
- README: install, data placement, quickstart, workflow diagram, how to add a new feature / strategy, how to interpret the gate.
- ARCHITECTURE.md: module diagram, data flow, interfaces.
- Run full test suite, ruff, type check; fix issues; final tag `v1.0.0`.
**Acceptance:** Fresh clone + `pip install -e .` + drop CSV in `data/raw` + `goldsys pipeline run --through validate` completes with reports; all tests pass.

---

## 8. NO-LOOK-AHEAD CHECKLIST (APPLIES TO EVERY SESSION)

- No negative shifts, no centered windows, no full-sample normalisation or percentiles; use expanding or rolling windows.
- HTF data is merged using only **completed** HTF bars (shift by one HTF bar).
- Swing/fractal/pattern features are timestamped at their **confirmation** bar.
- Signals use bar `t` close; fills occur at `t+1` open.
- Parameters, ML models and regime models are fit on the training window only and applied forward.
- Hold-out untouched until S12.

## 9. DEFINITION OF DONE (WHOLE PROJECT)

- [ ] All sessions S0-S14 acceptance criteria met, tests green.
- [ ] Quality report for the 2009-2025 data reviewed.
- [ ] Profiler report and `docs/hypotheses.md` populated.
- [ ] At least four strategies backtested with full reports.
- [ ] Validation gate results for each strategy on dev data.
- [ ] Hold-out evaluated exactly once per frozen strategy; verdicts recorded.
- [ ] Execution exports generated for approved strategies; paper runner parity verified.
- [ ] Documentation complete; reproducible from a clean clone.

## 10. HONEST EXPECTATIONS (DOCUMENT IN README)

Most hypotheses will fail the gate. That is the system working correctly. A strategy that survives costs, walk-forward, sensitivity, Monte Carlo and a one-shot hold-out has earned a paper-trading period (1-3 months) before any real capital. Past performance, even validated, does not guarantee future results.
