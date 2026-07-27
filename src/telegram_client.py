"""Shared Telegram notifier (same secrets as TRINITY-1)."""
import html
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message: str) -> bool:
        if not self.token or not self.chat_id:
            print("Telegram keys missing — print only:")
            print(message)
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": html.escape(message)[:4000],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        r = requests.post(url, json=payload, timeout=15)
        ok = r.status_code == 200
        print("Telegram sent" if ok else f"Telegram failed: {r.text}")
        return ok
