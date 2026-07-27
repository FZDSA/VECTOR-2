#!/usr/bin/env python3
"""Daily VECTOR-2 signal → Telegram (#2)."""
from datetime import datetime, timezone

from src.config import (
    BOT_ID, BOT_CODE, BOT_NAME, BOT_TAGLINE,
    START_DATE, LOOKBACK_DAYS, TOP_N, SMA_REGIME,
)
from src.universe import SP100, BENCHMARK, SAFE_ASSET
from src.data import download_prices
from src.strategy import select_portfolio, regime_on, momentum_scores
from src.telegram_client import TelegramBot


def main():
    tickers = list(dict.fromkeys(SP100 + [BENCHMARK, SAFE_ASSET]))
    px = download_prices(tickers, start=START_DATE)
    spy = px[BENCHMARK]
    panel = px.copy()
    if "GOOG" in panel.columns and "GOOGL" in panel.columns:
        panel = panel.drop(columns=["GOOG"])
    asof = panel.index[-1]

    on = regime_on(spy, asof)
    weights = select_portfolio(panel, spy, asof, safe_asset=SAFE_ASSET if SAFE_ASSET in panel.columns else None)
    scores = momentum_scores(panel.drop(columns=[SAFE_ASSET], errors="ignore"), asof)

    lines = [
        f"#{BOT_ID} {BOT_CODE} — {BOT_NAME}",
        BOT_TAGLINE + " (v1.2 inv-vol + BIL risk-off)",
        f"As of: {asof.date()}",
        f"Regime: {'RISK-ON' if on else 'RISK-OFF → ' + SAFE_ASSET}",
        f"Params: lookback={LOOKBACK_DAYS}d, top={TOP_N}, inv-vol weights",
        "",
    ]
    if weights:
        lines.append("Target weights:")
        for i, (t, w) in enumerate(sorted(weights.items(), key=lambda x: -x[1]), 1):
            sc = scores.get(t, float('nan'))
            mom = f" mom={sc*100:.1f}%" if t in scores.index else ""
            lines.append(f"  {i}. {t}  {w*100:.1f}%{mom}")
    else:
        lines.append("Target: 100% CASH")

    lines += [
        "",
        "Note: SIGNAL ONLY — no auto orders.",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    msg = "\n".join(lines)
    print(msg)
    TelegramBot().send_message(msg)


if __name__ == "__main__":
    main()
