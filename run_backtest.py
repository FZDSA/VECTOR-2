#!/usr/bin/env python3
"""Run VECTOR-2 historical backtest and save results."""
import json
from pathlib import Path

from src.config import START_DATE, BOT_CODE, LOOKBACK_DAYS, TOP_N, SMA_REGIME
from src.universe import SP100, BENCHMARK, SAFE_ASSET
from src.data import download_prices
from src.backtest import run_backtest


def main():
    out = Path("results")
    out.mkdir(exist_ok=True)

    tickers = list(dict.fromkeys(SP100 + [BENCHMARK, SAFE_ASSET]))
    print(f"Downloading {len(tickers)} symbols from Yahoo…")
    px = download_prices(tickers, start=START_DATE)
    if BENCHMARK not in px.columns:
        raise SystemExit("SPY missing")
    spy = px[BENCHMARK]
    stock_px = px.copy()
    # keep BIL + equities; drop all-nan cols
    stock_px = stock_px.loc[:, stock_px.notna().mean() > 0.85]
    # remove duplicate share-class if both present
    if "GOOG" in stock_px.columns and "GOOGL" in stock_px.columns:
        stock_px = stock_px.drop(columns=["GOOG"])

    print(f"Panel: {stock_px.shape[1]} cols, {len(stock_px)} days")
    print(f"Params: lookback={LOOKBACK_DAYS}, top={TOP_N}, SMA={SMA_REGIME}, safe={SAFE_ASSET}")

    res = run_backtest(stock_px, spy, safe_asset=SAFE_ASSET if SAFE_ASSET in stock_px.columns else None)

    res.equity.to_csv(out / "equity.csv", header=True)
    res.benchmark.to_csv(out / "benchmark.csv", header=True)
    res.trades.to_csv(out / "trades.csv", index=False)

    summary = {
        "bot": BOT_CODE,
        "version": "v1.2",
        "all": res.stats_all,
        "train_to_2021": res.stats_train,
        "test_from_2022": res.stats_test,
        "last_holdings": res.last_holdings,
        "n_rebalances": len(res.trades),
        "params": {
            "lookback": LOOKBACK_DAYS,
            "top_n": TOP_N,
            "sma": SMA_REGIME,
            "safe_asset": SAFE_ASSET,
            "weighting": "inverse_vol_63d",
            "abs_mom_filter": True,
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

    print("\n===", BOT_CODE, "v1.2 BACKTEST ===")
    print("ALL :", fmt(res.stats_all))
    print("TRAIN:", fmt(res.stats_train))
    print("TEST :", fmt(res.stats_test))
    print("Last:", ", ".join(res.last_holdings) or "CASH")
    excess = res.stats_test["cagr"] - res.stats_test["bench_cagr"]
    print(f"TEST excess vs SPY: {excess*100:+.1f}%")


if __name__ == "__main__":
    main()
