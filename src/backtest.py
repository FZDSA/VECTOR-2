"""Monthly rebalanced long-only backtest with costs."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.config import ONE_WAY_COST_BPS, TRAIN_END
from src.data import monthly_rebalance_dates
from src.strategy import select_portfolio


@dataclass
class BacktestResult:
    equity: pd.Series
    benchmark: pd.Series
    trades: pd.DataFrame
    stats_all: dict
    stats_train: dict
    stats_test: dict
    last_holdings: list[str]


def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def _ann_return(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)


def _sharpe(daily_ret: pd.Series) -> float:
    mu = daily_ret.mean()
    sd = daily_ret.std()
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float(mu / sd * np.sqrt(252))


def summarize(equity: pd.Series, benchmark: pd.Series) -> dict:
    rets = equity.pct_change().dropna()
    b = benchmark.reindex(equity.index).ffill()
    b_rets = b.pct_change().dropna()
    rets, b_rets = rets.align(b_rets, join="inner")
    excess = rets - b_rets
    return {
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1),
        "cagr": _ann_return(equity),
        "max_drawdown": _max_drawdown(equity),
        "sharpe": _sharpe(rets),
        "bench_cagr": _ann_return(b.dropna()),
        "bench_max_dd": _max_drawdown(b.dropna()),
        "bench_sharpe": _sharpe(b_rets),
        "avg_excess_daily": float(excess.mean()) if len(excess) else 0.0,
        "days": int(len(equity)),
    }


def run_backtest(prices: pd.DataFrame, spy: pd.Series, safe_asset: str | None = "BIL") -> BacktestResult:
    prices = prices.dropna(how="all")
    spy = spy.reindex(prices.index).ffill()
    rebalance_days = monthly_rebalance_dates(prices.index)
    min_start = prices.index[min(len(prices) - 1, 252)]
    rebalance_days = rebalance_days[rebalance_days >= min_start]

    cost = ONE_WAY_COST_BPS / 10000.0
    value = 1.0
    current_weights: dict[str, float] = {}
    trade_rows = []
    equity = []
    dates = []

    all_days = prices.index[prices.index >= rebalance_days[0]]
    reb_set = set(rebalance_days)

    for i, dt in enumerate(all_days):
        if dt in reb_set:
            target_w = select_portfolio(prices, spy, dt, safe_asset=safe_asset)
            keys = set(current_weights) | set(target_w)
            trade_cost = cost * sum(abs(target_w.get(k, 0) - current_weights.get(k, 0)) for k in keys)
            value *= (1.0 - trade_cost)
            turnover = 0.5 * sum(abs(target_w.get(k, 0) - current_weights.get(k, 0)) for k in keys)
            trade_rows.append({
                "date": dt.strftime("%Y-%m-%d"),
                "n_holdings": len(target_w),
                "holdings": ",".join(f"{k}:{target_w[k]:.2f}" for k in target_w),
                "turnover": round(turnover, 4),
                "cost": round(trade_cost, 6),
                "regime": "ON" if (safe_asset not in target_w or len(target_w) != 1) and target_w else ("SAFE" if target_w else "OFF"),
            })
            current_weights = target_w

        if i > 0:
            prev = all_days[i - 1]
            port_ret = 0.0
            for t, w in current_weights.items():
                if t in prices.columns and pd.notna(prices.at[dt, t]) and pd.notna(prices.at[prev, t]) and prices.at[prev, t] != 0:
                    port_ret += w * (prices.at[dt, t] / prices.at[prev, t] - 1.0)
            value *= (1.0 + port_ret)

        equity.append(value)
        dates.append(dt)

    eq = pd.Series(equity, index=pd.DatetimeIndex(dates), name="VECTOR-2")
    bench = (spy.reindex(eq.index).ffill() / spy.reindex(eq.index).ffill().iloc[0]).rename("SPY")
    trades = pd.DataFrame(trade_rows)

    stats_all = summarize(eq, bench)
    train_mask = eq.index <= pd.Timestamp(TRAIN_END)
    test_mask = eq.index > pd.Timestamp(TRAIN_END)
    stats_train = summarize(eq.loc[train_mask], bench.loc[train_mask]) if train_mask.any() else {}
    stats_test = summarize(eq.loc[test_mask], bench.loc[test_mask]) if test_mask.any() else {}
    last = list(current_weights.keys())
    return BacktestResult(eq, bench, trades, stats_all, stats_train, stats_test, last)
