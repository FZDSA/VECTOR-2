# VECTOR-2

Bot **#2** in the Investing fleet — cross-sectional **momentum** with a **SPY regime filter**.

| | |
|--|--|
| Code | `VECTOR-2` |
| Role | Research backtester + daily signal bot |
| Universe | S&P 100 (liquid) |
| Timeframe | Daily bars, **monthly** rebalance |
| Data | Yahoo Finance (`yfinance`) for research |
| Alerts | Same Telegram bot as TRINITY-1, prefixed `#2 VECTOR-2` |

## Strategy (v1.2)

1. Risk-on only when `SPY > SMA200`
2. Rank S&P 100 by 126-day return (skip most recent 21 days)
3. Hold top 10 with **inverse-vol** weights (and mom > 0)
4. If risk-off → **BIL** (T-bill ETF)
5. Costs: 10 bps one-way per turnover

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Full backtest (writes results/)
python run_backtest.py

# Today's signal → Telegram
python main_signal.py
```

## Relation to TRINITY-1

TRINITY-1 keeps running (AI hunter on Alpaca paper).  
VECTOR-2 is the edge-first research lane. Do not mix their orders until VECTOR proves itself.
