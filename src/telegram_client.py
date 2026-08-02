"""Shared Telegram notifier with HTML support."""
import html
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def telegram_reports_enabled() -> bool:
    """Group explanations off by default; set TELEGRAM_REPORTS=1 to re-enable."""
    return os.getenv("TELEGRAM_REPORTS", "0").strip().lower() in {"1", "true", "yes", "on"}


def esc(text) -> str:
    return html.escape(str(text), quote=False)


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message: str, *, as_html: bool = True) -> bool:
        if not telegram_reports_enabled():
            print("Telegram reports disabled (TELEGRAM_REPORTS≠1). Local log only.")
            print(message)
            return False
        if not self.token or not self.chat_id:
            print("Telegram keys missing — print only:")
            print(message)
            return False
        text = (message if as_html else html.escape(message))[:4000]
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        r = requests.post(url, json=payload, timeout=15)
        ok = r.status_code == 200
        print("Telegram sent" if ok else f"Telegram failed: {r.text}")
        return ok


def section(title: str, fa: str, body: str = "") -> str:
    parts = [f"<b>{esc(title)}</b>", f"<i>{esc(fa)}</i>"]
    if body:
        parts.append(body.rstrip())
    return "\n".join(parts)


def divider() -> str:
    return "────────────────"
