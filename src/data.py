"""Market data via Yahoo Finance."""
from __future__ import annotations

import time
from typing import Iterable

import pandas as pd
import yfinance as yf


def download_prices(tickers: Iterable[str], start: str, end: str | None = None) -> pd.DataFrame:
    """Return Adj Close panel (columns=tickers, index=dates)."""
    tickers = list(dict.fromkeys(tickers))
    # yfinance batch download
    df = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="column",
    )
    if df.empty:
        raise RuntimeError("No price data downloaded")

    if isinstance(df.columns, pd.MultiIndex):
        # columns like (Close, AAPL) or (AAPL, Close) depending on version
        if "Close" in df.columns.get_level_values(0):
            close = df["Close"].copy()
        elif "Close" in df.columns.get_level_values(1):
            close = df.xs("Close", axis=1, level=1).copy()
        else:
            # fallback first price field
            close = df.xs(df.columns.levels[0][0], axis=1, level=0).copy()
    else:
        close = df[["Close"]].copy() if "Close" in df.columns else df.copy()
        if len(tickers) == 1:
            close.columns = [tickers[0]]

    close = close.sort_index().ffill()
    # drop columns that are entirely NaN
    close = close.dropna(axis=1, how="all")
    return close


def monthly_rebalance_dates(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """First available trading day of each month in index."""
    s = pd.Series(index, index=index)
    # group by year-month, take first
    firsts = s.groupby([index.year, index.month]).first()
    return pd.DatetimeIndex(firsts.values)
