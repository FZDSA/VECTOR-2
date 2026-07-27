"""VECTOR-2 configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = 2
BOT_CODE = "VECTOR-2"
BOT_NAME = "Vector"
BOT_TAGLINE = "Cross-sectional momentum + SPY regime filter"

# Strategy
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "252"))  # ~6 months
SKIP_RECENT_DAYS = int(os.getenv("SKIP_RECENT_DAYS", "0"))  # classic momentum skip
SMA_REGIME = int(os.getenv("SMA_REGIME", "200"))
TOP_N = int(os.getenv("TOP_N", "10"))
ONE_WAY_COST_BPS = float(os.getenv("ONE_WAY_COST_BPS", "10"))  # 0.10%

# Backtest window
START_DATE = os.getenv("START_DATE", "2015-01-01")
TRAIN_END = os.getenv("TRAIN_END", "2021-12-31")  # in-sample ends
# out-of-sample = after TRAIN_END

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
