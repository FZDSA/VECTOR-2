#!/usr/bin/env python3
"""Daily VECTOR-2 signal → pretty Telegram (#2)."""
from datetime import datetime, timezone

from src.config import (
    BOT_ID,
    BOT_CODE,
    BOT_NAME,
    BOT_TAGLINE,
    START_DATE,
    LOOKBACK_DAYS,
    TOP_N,
    SMA_REGIME,
)
from src.universe import SP100, BENCHMARK, SAFE_ASSET
from src.data import download_prices
from src.strategy import select_portfolio, regime_on, momentum_scores
from src.telegram_client import TelegramBot, esc, section, divider


def build_vector_report(asof, on: bool, weights: dict, scores) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    regime_title = (
        f"رژیم بازار: RISK-ON (SPY بالای SMA{SMA_REGIME})"
        if on
        else f"رژیم بازار: RISK-OFF → {SAFE_ASSET}"
    )
    regime_fa = (
        "توضیح: بازار از نظر روند بلندمدت قابل‌قبول است؛ اجازهٔ نگه‌داشتن سهام مومنتوم را می‌دهد."
        if on
        else f"توضیح: روند کلی بازار ضعیف است؛ به‌جای سهام، دارایی امن‌تر ({SAFE_ASSET} ≈ خزانه کوتاه‌مدت) پیشنهاد می‌شود."
    )

    blocks = [
        f"<b>#{BOT_ID} {esc(BOT_CODE)}</b>  ·  {esc(BOT_NAME)}",
        f"<i>{esc(BOT_TAGLINE)}</i>",
        "<i>ربات سیگنال مومنتوم — سفارش خودکار نمی‌گذارد</i>",
        divider(),
        section(
            f"تاریخ داده: {asof.date()}",
            "توضیح: آخرین روز معاملاتی موجود در دادهٔ Yahoo برای محاسبهٔ سیگنال.",
        ),
        divider(),
        section(regime_title, regime_fa),
        divider(),
        section(
            f"تنظیمات: lookback={LOOKBACK_DAYS}d · top={TOP_N} · وزن=inv-vol",
            "توضیح: بازده حدود ۱۲ ماه گذشته رتبه‌بندی می‌شود؛ ۱۰ تای برتر با وزن معکوس‌نوسان چیده می‌شوند.",
        ),
        divider(),
    ]

    if weights:
        lines = []
        only_safe = list(weights.keys()) == [SAFE_ASSET]
        if only_safe:
            lines.append(f"🎯 هدف: ۱۰۰٪ <code>{esc(SAFE_ASSET)}</code>")
            lines.append(
                f"<i>توضیح: در حالت ترس، کل سبد پیشنهادی روی {SAFE_ASSET} است.</i>"
            )
        else:
            lines.append("<b>سبد پیشنهادی (وزن‌ها)</b>")
            lines.append(
                "<i>توضیح: درصد یعنی سهم از سبد. mom = بازده تقریبی ۱۲ماهه.</i>"
            )
            lines.append("")
            for i, (t, w) in enumerate(sorted(weights.items(), key=lambda x: -x[1]), 1):
                if t in getattr(scores, "index", []):
                    mom = f"  ·  mom {scores.get(t)*100:.1f}%"
                else:
                    mom = ""
                bar = "▓" * max(1, int(round(w * 10))) + "░" * (10 - max(1, int(round(w * 10))))
                lines.append(
                    f"{i}. <code>{esc(t)}</code>  <b>{w*100:.1f}%</b>  {bar}{mom}"
                )
        body = "\n".join(lines)
    else:
        body = "هدف: ۱۰۰٪ نقد\n<i>توضیح: هیچ سهم/دارایی امنی انتخاب نشد.</i>"

    blocks.append(
        section(
            "خروجی سیگنال",
            "توضیح: این یک پیشنهاد پژوهشی است؛ خودت تصمیم بگیر اجرا کنی یا نه.",
            body,
        )
    )
    blocks.append(divider())
    blocks.append(
        section(
            "یادآوری مهم",
            "توضیح: VECTOR-2 فعلاً فقط پیام می‌دهد. خرید/فروش خودکار ندارد (برخلاف ربات ۱).",
        )
    )
    blocks.append(f"<i>زمان گزارش: {esc(now)}</i>")
    blocks.append("<i>این پیام خلاصهٔ ربات شماره ۲ است.</i>")
    return "\n".join(blocks)


def main():
    tickers = list(dict.fromkeys(SP100 + [BENCHMARK, SAFE_ASSET]))
    px = download_prices(tickers, start=START_DATE)
    spy = px[BENCHMARK]
    panel = px.copy()
    if "GOOG" in panel.columns and "GOOGL" in panel.columns:
        panel = panel.drop(columns=["GOOG"])
    asof = panel.index[-1]

    on = regime_on(spy, asof)
    weights = select_portfolio(
        panel,
        spy,
        asof,
        safe_asset=SAFE_ASSET if SAFE_ASSET in panel.columns else None,
    )
    scores = momentum_scores(
        panel.drop(columns=[SAFE_ASSET], errors="ignore"), asof
    )

    msg = build_vector_report(asof, on, weights, scores)
    print(msg)
    TelegramBot().send_message(msg, as_html=True)


if __name__ == "__main__":
    main()
