# VECTOR-2 Backtest Report (v1.2)

## Changes vs v1.1
- Inverse-volatility (63d) weights instead of equal weight
- Absolute momentum filter (mom > 0)
- Risk-off allocates to **BIL** (T-bills) instead of idle cash
- Drop duplicate GOOG when GOOGL present

## Results

| Period | CAGR | MaxDD | Sharpe | SPY CAGR | Excess |
|--------|------|-------|--------|----------|--------|
| All | 17.2% | -29.8% | 0.89 | 15.0% | +2.2% |
| Train ≤2021 | 18.5% | -29.8% | 0.87 | 17.6% | +0.9% |
| Test ≥2022 | 15.1% | -21.0% | 0.90 | 11.5% | +3.6% |
