"""Momentum + regime + sector caps + liquidity + vol targeting (v1.3)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import (
    LOOKBACK_DAYS,
    SKIP_RECENT_DAYS,
    SMA_REGIME,
    TOP_N,
    CANDIDATE_POOL,
    MAX_PER_SECTOR,
    MAX_SECTOR_WEIGHT,
    MIN_ADV_DOLLARS,
    TARGET_ANNUAL_VOL,
    VOL_WINDOW,
    ADV_WINDOW,
)
from src.universe import sector_of


def regime_on(spy: pd.Series, asof: pd.Timestamp) -> bool:
    hist = spy.loc[:asof].dropna()
    if len(hist) < SMA_REGIME + 5:
        return False
    sma = hist.rolling(SMA_REGIME).mean().iloc[-1]
    return bool(hist.iloc[-1] > sma)


def momentum_scores(prices: pd.DataFrame, asof: pd.Timestamp) -> pd.Series:
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


def avg_dollar_volume(
    prices: pd.DataFrame, volume: pd.DataFrame | None, asof: pd.Timestamp
) -> pd.Series:
    if volume is None or volume.empty:
        return pd.Series(dtype=float)
    px = prices.loc[:asof].iloc[-ADV_WINDOW:]
    vol = volume.reindex(px.index).reindex(columns=px.columns).fillna(0)
    adv = (px * vol).mean()
    return adv.dropna()


def inv_vol_weights(
    prices: pd.DataFrame, tickers: list[str], asof: pd.Timestamp, vol_window: int = VOL_WINDOW
) -> dict[str, float]:
    if not tickers:
        return {}
    hist = prices.loc[:asof, tickers].dropna(how="all")
    if len(hist) < vol_window + 2:
        w = 1.0 / len(tickers)
        return {t: w for t in tickers}
    rets = hist.pct_change().iloc[-vol_window:]
    vol = rets.std().replace(0, np.nan)
    inv = (1.0 / vol).replace([np.inf, -np.inf], np.nan).dropna()
    if inv.empty:
        w = 1.0 / len(tickers)
        return {t: w for t in tickers}
    inv = inv / inv.sum()
    return {t: float(inv[t]) for t in inv.index}


def _apply_sector_weight_cap(weights: dict[str, float]) -> dict[str, float]:
    """Cap total weight per sector; renormalize remainder among uncapped names."""
    if not weights:
        return {}
    w = dict(weights)
    for _ in range(8):
        sector_sum: dict[str, float] = {}
        for t, wt in w.items():
            sector_sum[sector_of(t)] = sector_sum.get(sector_of(t), 0.0) + wt
        overweight = {s: tot for s, tot in sector_sum.items() if tot > MAX_SECTOR_WEIGHT + 1e-9}
        if not overweight:
            break
        for sec, tot in overweight.items():
            scale = MAX_SECTOR_WEIGHT / tot
            for t in list(w):
                if sector_of(t) == sec:
                    w[t] *= scale
        # renormalize to 1
        s = sum(w.values())
        if s > 0:
            w = {t: wt / s for t, wt in w.items()}
    return w


def _vol_target(
    prices: pd.DataFrame,
    weights: dict[str, float],
    asof: pd.Timestamp,
    safe_asset: str | None,
) -> dict[str, float]:
    """Scale equity book to target annualized vol; residual -> safe_asset/cash."""
    if TARGET_ANNUAL_VOL <= 0:
        return dict(weights)
    if not weights:
        return {}
    tickers = [t for t in weights if t != safe_asset]
    if not tickers:
        return dict(weights)

    hist = prices.loc[:asof, tickers].dropna(how="all")
    if len(hist) < VOL_WINDOW + 2:
        return dict(weights)

    rets = hist.pct_change().iloc[-VOL_WINDOW:].dropna(how="all")
    w = np.array([weights[t] for t in tickers], dtype=float)
    rets = rets.reindex(columns=tickers).fillna(0.0)
    cov = np.cov(rets.to_numpy().T)
    if cov.ndim == 0:
        return dict(weights)
    port_var = float(w @ cov @ w)
    port_vol = np.sqrt(max(port_var, 0.0)) * np.sqrt(252)
    if port_vol <= 1e-8:
        return dict(weights)

    scale = min(1.0, TARGET_ANNUAL_VOL / port_vol)
    out = {t: weights[t] * scale for t in tickers}
    residual = 1.0 - sum(out.values())
    if residual > 1e-6 and safe_asset and safe_asset in prices.columns:
        out[safe_asset] = out.get(safe_asset, 0.0) + residual
    return out


def select_names(
    prices: pd.DataFrame,
    asof: pd.Timestamp,
    scores: pd.Series,
    volume: pd.DataFrame | None = None,
) -> list[str]:
    """Liquidity + sector-count constrained top names."""
    if scores.empty:
        return []

    adv = avg_dollar_volume(prices, volume, asof)
    ordered = list(scores.head(CANDIDATE_POOL).index)
    picks: list[str] = []
    sector_count: dict[str, int] = {}

    for t in ordered:
        if t not in prices.columns:
            continue
        if not adv.empty and t in adv.index and adv[t] < MIN_ADV_DOLLARS:
            continue
        sec = sector_of(t)
        if sector_count.get(sec, 0) >= MAX_PER_SECTOR:
            continue
        picks.append(t)
        sector_count[sec] = sector_count.get(sec, 0) + 1
        if len(picks) >= TOP_N:
            break
    return picks


def select_portfolio(
    prices: pd.DataFrame,
    spy: pd.Series,
    asof: pd.Timestamp,
    safe_asset: str | None = None,
    require_positive_mom: bool = True,
    volume: pd.DataFrame | None = None,
) -> dict[str, float]:
    """Return target weights with v1.3 controls."""
    if not regime_on(spy, asof):
        if safe_asset and safe_asset in prices.columns:
            return {safe_asset: 1.0}
        return {}

    scores = momentum_scores(prices, asof)
    if safe_asset:
        scores = scores.drop(labels=[safe_asset], errors="ignore")
        # also drop benchmark if present in panel
        scores = scores.drop(labels=["SPY"], errors="ignore")
    if require_positive_mom:
        scores = scores[scores > 0]
    if scores.empty:
        if safe_asset and safe_asset in prices.columns:
            return {safe_asset: 1.0}
        return {}

    picks = select_names(prices, asof, scores, volume=volume)
    if not picks:
        if safe_asset and safe_asset in prices.columns:
            return {safe_asset: 1.0}
        return {}

    weights = inv_vol_weights(prices, picks, asof)
    weights = _apply_sector_weight_cap(weights)
    weights = _vol_target(prices, weights, asof, safe_asset=safe_asset)
    return weights
