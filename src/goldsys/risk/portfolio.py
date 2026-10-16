import pandas as pd


def combine_equity(equity_curves: dict[str, pd.Series]) -> pd.DataFrame:
    frame = pd.concat(equity_curves, axis=1).sort_index().ffill()
    frame["combined"] = frame.sum(axis=1)
    returns = frame.drop(columns="combined").pct_change().dropna()
    correlation = returns.corr()
    return frame, correlation
