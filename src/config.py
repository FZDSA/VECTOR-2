"""VECTOR-2 configuration (v1.3)."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = 2
BOT_CODE = "VECTOR-2"
BOT_NAME = "Vector"
BOT_TAGLINE = "Momentum + regime + sector/liquidity controls"

# Strategy core
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "252"))
SKIP_RECENT_DAYS = int(os.getenv("SKIP_RECENT_DAYS", "0"))
SMA_REGIME = int(os.getenv("SMA_REGIME", "200"))
TOP_N = int(os.getenv("TOP_N", "10"))
ONE_WAY_COST_BPS = float(os.getenv("ONE_WAY_COST_BPS", "10"))

# v1.3 risk upgrades
CANDIDATE_POOL = int(os.getenv("CANDIDATE_POOL", "40"))  # rank top K then apply filters
MAX_PER_SECTOR = int(os.getenv("MAX_PER_SECTOR", "3"))
MAX_SECTOR_WEIGHT = float(os.getenv("MAX_SECTOR_WEIGHT", "0.30"))
MIN_ADV_DOLLARS = float(os.getenv("MIN_ADV_DOLLARS", "5e7"))  # $50M 20d ADV
# 0 = disabled (better absolute CAGR in our tests). Set e.g. 0.12 to enable.
TARGET_ANNUAL_VOL = float(os.getenv("TARGET_ANNUAL_VOL", "0"))
VOL_WINDOW = int(os.getenv("VOL_WINDOW", "63"))
ADV_WINDOW = int(os.getenv("ADV_WINDOW", "20"))

# Backtest window
START_DATE = os.getenv("START_DATE", "2015-01-01")
TRAIN_END = os.getenv("TRAIN_END", "2021-12-31")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
