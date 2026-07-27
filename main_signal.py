#!/usr/bin/env python3
"""Daily VECTOR-2 signal → Telegram (#2)."""
from datetime import datetime, timezone

from src.config import (
    BOT_ID, BOT_CODE, BOT_NAME, BOT_TAGLINE,
    START_DATE, LOOKBACK_DAYS, TOP_N, SMA_REGIME,
)
from src.universe import SP100, BENCHMARK
from src.data import download_prices
from src.strategy import select_portfolio, regime_on, momentum_scores
from src.telegram_client import TelegramBot


def main():
    tickers = SP100 + [BENCHMARK]
    px = download_prices(tickers, start=START_DATE)
    spy = px[BENCHMARK]
    stocks = px.drop(columns=[BENCHMARK], errors="ignore")
    asof = stocks.index[-1]

    on = regime_on(spy, asof)
    holdings = select_portfolio(stocks, spy, asof)
    scores = momentum_scores(stocks, asof)

    lines = [
        f"#{BOT_ID} {BOT_CODE} — {BOT_NAME}",
        BOT_TAGLINE,
        f"As of: {asof.date()}",
        f"Regime: {'RISK-ON (SPY > SMA' + str(SMA_REGIME) + ')' if on else 'RISK-OFF → CASH'}",
        f"Params: lookback={LOOKBACK_DAYS}d, top={TOP_N}",
        "",
    ]
    if holdings:
        lines.append("Target holdings (equal weight):")
        for i, t in enumerate(holdings, 1):
            sc = scores.get(t, float("nan"))
            lines.append(f"  {i}. {t}  mom={sc*100:.1f}%")
    else:
        lines.append("Target: 100% CASH")

    lines += [
        "",
        "Note: SIGNAL ONLY — no auto orders yet.",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    msg = "\n".join(lines)
    print(msg)
    TelegramBot().send_message(msg)


if __name__ == "__main__":
    main()
