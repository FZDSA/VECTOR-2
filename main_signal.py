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
    MAX_PER_SECTOR,
    MAX_SECTOR_WEIGHT,
    TARGET_ANNUAL_VOL,
)
from src.universe import SP100, BENCHMARK, SAFE_ASSET, sector_of
from src.data import download_close_and_volume
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
        else f"توضیح: روند کلی بازار ضعیف است؛ به‌جای سهام، دارایی امن‌تر ({SAFE_ASSET}) پیشنهاد می‌شود."
    )

    blocks = [
        f"<b>#{BOT_ID} {esc(BOT_CODE)}</b>  ·  {esc(BOT_NAME)}  ·  v1.3",
        f"<i>{esc(BOT_TAGLINE)}</i>",
        "<i>ربات سیگنال مومنتوم — سفارش خودکار نمی‌گذارد</i>",
        divider(),
        section(
            f"تاریخ داده: {asof.date()}",
            "توضیح: آخرین روز معاملاتی موجود برای محاسبهٔ سیگنال.",
        ),
        divider(),
        section(regime_title, regime_fa),
        divider(),
        section(
            (
                f"تنظیمات: lookback={LOOKBACK_DAYS}d · top={TOP_N} · "
                f"max/sector={MAX_PER_SECTOR} · sector≤{int(MAX_SECTOR_WEIGHT*100)}%"
                + (f" · vol≈{int(TARGET_ANNUAL_VOL*100)}%" if TARGET_ANNUAL_VOL > 0 else "")
            ),
            "توضیح: مومنتوم + سقف تعداد/وزن هر بخش + فیلتر نقدشوندگی"
            + (" + هدف نوسان سبد." if TARGET_ANNUAL_VOL > 0 else "."),
        ),
        divider(),
    ]

    if weights:
        lines = []
        only_safe = set(weights) <= {SAFE_ASSET}
        if only_safe:
            lines.append(f"🎯 هدف: ۱۰۰٪ <code>{esc(SAFE_ASSET)}</code>")
        else:
            lines.append("<b>سبد پیشنهادی (وزن‌ها)</b>")
            lines.append(
                "<i>توضیح: درصد = سهم از سبد. sec = بخش. mom = بازده تقریبی ۱۲ماهه.</i>"
            )
            lines.append("")
            for i, (t, w) in enumerate(sorted(weights.items(), key=lambda x: -x[1]), 1):
                if t in getattr(scores, "index", []):
                    mom = f" · mom {scores.get(t)*100:.1f}%"
                else:
                    mom = ""
                sec = sector_of(t) if t != SAFE_ASSET else "Safe"
                bar_n = max(1, min(10, int(round(w * 10))))
                bar = "▓" * bar_n + "░" * (10 - bar_n)
                lines.append(
                    f"{i}. <code>{esc(t)}</code> [{esc(sec)}] "
                    f"<b>{w*100:.1f}%</b> {bar}{mom}"
                )
        body = "\n".join(lines)
    else:
        body = "هدف: ۱۰۰٪ نقد"

    blocks.append(
        section(
            "خروجی سیگنال",
            "توضیح: پیشنهاد پژوهشی است؛ اجرای واقعی اختیاری است.",
            body,
        )
    )
    blocks.append(divider())
    blocks.append(
        section(
            "یادآوری مهم",
            "توضیح: VECTOR-2 فعلاً فقط پیام می‌دهد و خرید/فروش خودکار ندارد.",
        )
    )
    blocks.append(f"<i>زمان گزارش: {esc(now)}</i>")
    blocks.append("<i>این پیام خلاصهٔ ربات شماره ۲ است.</i>")
    return "\n".join(blocks)


def main():
    tickers = list(dict.fromkeys(SP100 + [BENCHMARK, SAFE_ASSET]))
    close, volume = download_close_and_volume(tickers, start=START_DATE)
    spy = close[BENCHMARK]
    panel = close.copy()
    if "GOOG" in panel.columns and "GOOGL" in panel.columns:
        panel = panel.drop(columns=["GOOG"])
    volume = volume.reindex(columns=panel.columns).fillna(0)
    asof = panel.index[-1]

    on = regime_on(spy, asof)
    weights = select_portfolio(
        panel,
        spy,
        asof,
        safe_asset=SAFE_ASSET if SAFE_ASSET in panel.columns else None,
        volume=volume,
    )
    scores = momentum_scores(
        panel.drop(columns=[SAFE_ASSET, BENCHMARK], errors="ignore"), asof
    )

    msg = build_vector_report(asof, on, weights, scores)
    print(msg)
    TelegramBot().send_message(msg, as_html=True)


if __name__ == "__main__":
    main()
