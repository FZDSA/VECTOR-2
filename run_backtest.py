#!/usr/bin/env python3
"""Run VECTOR-2 historical backtest and save results."""
import json
from pathlib import Path

import pandas as pd

from src.config import START_DATE, BOT_CODE, LOOKBACK_DAYS, TOP_N, SMA_REGIME
from src.universe import SP100, BENCHMARK
from src.data import download_prices
from src.backtest import run_backtest


def main():
    out = Path("results")
    out.mkdir(exist_ok=True)

    tickers = SP100 + [BENCHMARK]
    print(f"Downloading {len(tickers)} symbols from Yahoo…")
    px = download_prices(tickers, start=START_DATE)
    if BENCHMARK not in px.columns:
        raise SystemExit("SPY missing from download")
    spy = px[BENCHMARK]
    stock_px = px.drop(columns=[BENCHMARK], errors="ignore")
    # drop tickers with too many missing
    stock_px = stock_px.loc[:, stock_px.notna().mean() > 0.9]

    print(f"Universe after clean: {stock_px.shape[1]} names, {len(stock_px)} days")
    print(f"Params: lookback={LOOKBACK_DAYS}, top={TOP_N}, SMA={SMA_REGIME}")

    res = run_backtest(stock_px, spy)

    res.equity.to_csv(out / "equity.csv", header=True)
    res.benchmark.to_csv(out / "benchmark.csv", header=True)
    res.trades.to_csv(out / "trades.csv", index=False)

    summary = {
        "bot": BOT_CODE,
        "all": res.stats_all,
        "train_to_2021": res.stats_train,
        "test_from_2022": res.stats_test,
        "last_holdings": res.last_holdings,
        "n_rebalances": len(res.trades),
        "params": {
            "lookback": LOOKBACK_DAYS,
            "top_n": TOP_N,
            "sma": SMA_REGIME,
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))

    def fmt(s):
        if not s:
            return "n/a"
        return (
            f"CAGR {s['cagr']*100:.1f}% | MaxDD {s['max_drawdown']*100:.1f}% | "
            f"Sharpe {s['sharpe']:.2f} | vs SPY CAGR {s['bench_cagr']*100:.1f}%"
        )

    print("\n===", BOT_CODE, "BACKTEST ===")
    print("ALL :", fmt(res.stats_all))
    print("TRAIN:", fmt(res.stats_train))
    print("TEST :", fmt(res.stats_test))
    print("Last holdings:", ", ".join(res.last_holdings) or "CASH")
    print("Wrote results/summary.json")


if __name__ == "__main__":
    main()
