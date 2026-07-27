"""Momentum + regime signal logic (v1.2)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import LOOKBACK_DAYS, SKIP_RECENT_DAYS, SMA_REGIME, TOP_N


def regime_on(spy: pd.Series, asof: pd.Timestamp) -> bool:
    hist = spy.loc[:asof].dropna()
    if len(hist) < SMA_REGIME + 5:
        return False
    sma = hist.rolling(SMA_REGIME).mean().iloc[-1]
    return bool(hist.iloc[-1] > sma)


def momentum_scores(prices: pd.DataFrame, asof: pd.Timestamp) -> pd.Series:
    """Return lookback return ending SKIP_RECENT_DAYS before asof."""
    hist = prices.loc[:asof]
    need = LOOKBACK_DAYS + SKIP_RECENT_DAYS + 5
    if len(hist) < need:
        return pd.Series(dtype=float)

    if SKIP_RECENT_DAYS > 0:
        end_idx = -SKIP_RECENT_DAYS
        end_px = hist.iloc[end_idx]
        start_px = hist.iloc[end_idx - LOOKBACK_DAYS]
    else:
        end_px = hist.iloc[-1]
        start_px = hist.iloc[-1 - LOOKBACK_DAYS]

    scores = (end_px / start_px) - 1.0
    return scores.dropna().sort_values(ascending=False)


def inv_vol_weights(prices: pd.DataFrame, tickers: list[str], asof: pd.Timestamp, vol_window: int = 63) -> dict[str, float]:
    """Inverse-volatility weights (63d) over selected tickers."""
    if not tickers:
        return {}
    hist = prices.loc[:asof, tickers].dropna(how="all")
    if len(hist) < vol_window + 2:
        w = 1.0 / len(tickers)
        return {t: w for t in tickers}
    rets = hist.pct_change().iloc[-vol_window:]
    vol = rets.std().replace(0, np.nan)
    inv = 1.0 / vol
    inv = inv.replace([np.inf, -np.inf], np.nan).dropna()
    if inv.empty:
        w = 1.0 / len(tickers)
        return {t: w for t in tickers}
    inv = inv / inv.sum()
    return {t: float(inv[t]) for t in inv.index}


def select_portfolio(
    prices: pd.DataFrame,
    spy: pd.Series,
    asof: pd.Timestamp,
    safe_asset: str | None = None,
    require_positive_mom: bool = True,
) -> dict[str, float]:
    """Return target weights. Risk-off -> safe_asset (or empty cash)."""
    if not regime_on(spy, asof):
        if safe_asset and safe_asset in prices.columns:
            return {safe_asset: 1.0}
        return {}

    scores = momentum_scores(prices, asof)
    # never rank the safe asset as equity momentum name
    if safe_asset:
        scores = scores.drop(labels=[safe_asset], errors="ignore")
    if require_positive_mom:
        scores = scores[scores > 0]
    if scores.empty:
        if safe_asset and safe_asset in prices.columns:
            return {safe_asset: 1.0}
        return {}

    picks = list(scores.head(TOP_N).index)
    return inv_vol_weights(prices, picks, asof)
