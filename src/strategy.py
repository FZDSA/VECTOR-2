"""Momentum + regime signal logic."""
from __future__ import annotations

import pandas as pd

from src.config import LOOKBACK_DAYS, SKIP_RECENT_DAYS, SMA_REGIME, TOP_N


def regime_on(spy: pd.Series, asof: pd.Timestamp) -> bool:
    hist = spy.loc[:asof].dropna()
    if len(hist) < SMA_REGIME + 5:
        return False
    sma = hist.rolling(SMA_REGIME).mean().iloc[-1]
    return bool(hist.iloc[-1] > sma)


def momentum_scores(prices: pd.DataFrame, asof: pd.Timestamp) -> pd.Series:
    """126d return ending SKIP_RECENT_DAYS before asof."""
    hist = prices.loc[:asof]
    if len(hist) < LOOKBACK_DAYS + SKIP_RECENT_DAYS + 5:
        return pd.Series(dtype=float)

    # end point: skip recent month
    if SKIP_RECENT_DAYS > 0:
        end_idx = -SKIP_RECENT_DAYS
        end_px = hist.iloc[end_idx]
        start_px = hist.iloc[end_idx - LOOKBACK_DAYS]
    else:
        end_px = hist.iloc[-1]
        start_px = hist.iloc[-1 - LOOKBACK_DAYS]

    scores = (end_px / start_px) - 1.0
    return scores.dropna().sort_values(ascending=False)


def select_portfolio(prices: pd.DataFrame, spy: pd.Series, asof: pd.Timestamp) -> list[str]:
    if not regime_on(spy, asof):
        return []  # cash
    scores = momentum_scores(prices, asof)
    if scores.empty:
        return []
    return list(scores.head(TOP_N).index)
