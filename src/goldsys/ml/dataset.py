import numpy as np
import pandas as pd


def build_signal_dataset(signals, features, trades):
    rows = []
    trade_rows = trades.set_index("signal_time") if not trades.empty and "signal_time" in trades else pd.DataFrame()
    for signal in signals:
        if signal.time not in features.index or signal.time not in trade_rows.index:
            continue
        values = features.loc[signal.time]
        row = {k: v for k, v in values.items() if np.isscalar(v) and not isinstance(v, (str, bool))}
        trade = trade_rows.loc[signal.time]
        if isinstance(trade, pd.DataFrame):
            trade = trade.iloc[0]
        row.update({"signal_time": signal.time, "r_multiple": float(trade.r_multiple),
                    "label": int(float(trade.r_multiple) > 0)})
        rows.append(row)
    return pd.DataFrame(rows)


def purged_folds(data, n_splits=5, embargo=0):
    """Yield train/test positions with a temporal embargo around each test fold."""
    n = len(data)
    for fold in np.array_split(np.arange(n), n_splits):
        if not len(fold):
            continue
        test_start, test_end = int(fold[0]), int(fold[-1])
        test = np.arange(test_start, test_end + 1)
        train = np.concatenate([np.arange(0, max(0, test_start - embargo)),
                                np.arange(min(n, test_end + 1 + embargo), n)])
        yield train, test
