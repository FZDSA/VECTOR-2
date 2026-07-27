#!/usr/bin/env python3
"""Run VECTOR-2 historical backtest and save results."""
import json
from pathlib import Path

from src.config import (
    START_DATE,
    BOT_CODE,
    LOOKBACK_DAYS,
    TOP_N,
    SMA_REGIME,
    MAX_PER_SECTOR,
    MAX_SECTOR_WEIGHT,
    TARGET_ANNUAL_VOL,
    MIN_ADV_DOLLARS,
)
from src.universe import SP100, BENCHMARK, SAFE_ASSET
from src.data import download_close_and_volume
from src.backtest import run_backtest


def main():
    out = Path("results")
    out.mkdir(exist_ok=True)

    tickers = list(dict.fromkeys(SP100 + [BENCHMARK, SAFE_ASSET]))
    print(f"Downloading {len(tickers)} symbols from Yahoo…")
    close, volume = download_close_and_volume(tickers, start=START_DATE)
    if BENCHMARK not in close.columns:
        raise SystemExit("SPY missing")
    spy = close[BENCHMARK]
    stock_px = close.copy()
    stock_px = stock_px.loc[:, stock_px.notna().mean() > 0.85]
    if "GOOG" in stock_px.columns and "GOOGL" in stock_px.columns:
        stock_px = stock_px.drop(columns=["GOOG"])
    volume = volume.reindex(columns=stock_px.columns).fillna(0)

    print(f"Panel: {stock_px.shape[1]} cols, {len(stock_px)} days")
    print(
        f"Params v1.3: lookback={LOOKBACK_DAYS}, top={TOP_N}, SMA={SMA_REGIME}, "
        f"max/sector={MAX_PER_SECTOR}, sector_w≤{MAX_SECTOR_WEIGHT}, "
        f"target_vol={TARGET_ANNUAL_VOL}, min_ADV=${MIN_ADV_DOLLARS:,.0f}"
    )

    res = run_backtest(
        stock_px,
        spy,
        safe_asset=SAFE_ASSET if SAFE_ASSET in stock_px.columns else None,
        volume=volume,
    )

    res.equity.to_csv(out / "equity.csv", header=True)
    res.benchmark.to_csv(out / "benchmark.csv", header=True)
    res.trades.to_csv(out / "trades.csv", index=False)

    summary = {
        "bot": BOT_CODE,
        "version": "v1.3",
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
            "max_per_sector": MAX_PER_SECTOR,
            "max_sector_weight": MAX_SECTOR_WEIGHT,
            "target_annual_vol": TARGET_ANNUAL_VOL,
            "min_adv_dollars": MIN_ADV_DOLLARS,
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

    print("\n===", BOT_CODE, "v1.3 BACKTEST ===")
    print("ALL :", fmt(res.stats_all))
    print("TRAIN:", fmt(res.stats_train))
    print("TEST :", fmt(res.stats_test))
    print("Last:", ", ".join(res.last_holdings) or "CASH")
    excess = res.stats_test["cagr"] - res.stats_test["bench_cagr"]
    print(f"TEST excess vs SPY: {excess*100:+.1f}%")


if __name__ == "__main__":
    main()
