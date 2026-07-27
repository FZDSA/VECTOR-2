"""Market data via Yahoo Finance."""
from __future__ import annotations

from typing import Iterable

import pandas as pd
import yfinance as yf


def _extract_field(df: pd.DataFrame, field: str, tickers: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        level0 = df.columns.get_level_values(0)
        level1 = df.columns.get_level_values(1)
        if field in level0:
            out = df[field].copy()
        elif field in level1:
            out = df.xs(field, axis=1, level=1).copy()
        else:
            raise KeyError(f"{field} not in download columns")
    else:
        if field in df.columns:
            out = df[[field]].copy()
            if len(tickers) == 1:
                out.columns = [tickers[0]]
        else:
            raise KeyError(f"{field} not in download columns")
    return out.sort_index()


def download_prices(tickers: Iterable[str], start: str, end: str | None = None) -> pd.DataFrame:
    """Return adjusted Close panel (columns=tickers)."""
    close, _ = download_close_and_volume(tickers, start=start, end=end)
    return close


def download_close_and_volume(
    tickers: Iterable[str], start: str, end: str | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (Close, Volume) panels aligned on dates."""
    tickers = list(dict.fromkeys(tickers))
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

    close = _extract_field(df, "Close", tickers).ffill().dropna(axis=1, how="all")
    try:
        volume = _extract_field(df, "Volume", tickers).fillna(0)
        volume = volume.reindex(columns=close.columns).fillna(0)
    except KeyError:
        volume = pd.DataFrame(0.0, index=close.index, columns=close.columns)
    return close, volume


def monthly_rebalance_dates(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """First available trading day of each month in index."""
    s = pd.Series(index, index=index)
    firsts = s.groupby([index.year, index.month]).first()
    return pd.DatetimeIndex(firsts.values)
