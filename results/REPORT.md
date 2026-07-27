# VECTOR-2 Backtest Report (v1.1)

Generated locally from Yahoo daily data.

## Rules
- Universe: S&P 100 liquid names
- Timeframe: daily, monthly rebalance
- Momentum: 252-day return (no skip month)
- Regime: risk-on only if SPY > SMA200 else cash
- Portfolio: top 10 equal weight
- Cost: 10 bps one-way

## Results

| Period | CAGR | MaxDD | Sharpe | SPY CAGR |
|--------|------|-------|--------|----------|
| All | 18.3% | -33.2% | 0.87 | 15.0% |
| Train ≤2021 | 22.0% | -33.2% | 0.96 | 17.6% |
| Test ≥2022 | 13.0% | -26.2% | 0.73 | 11.5% |

## Notes
- v1 (126d + skip 21d) **lost** to SPY out-of-sample.
- v1.1 (252d, no skip) **slightly beat** SPY in 2022+ sample (+~1.5% CAGR) with similar DD.
- This is research-grade, not proof of future alpha. Signal-only until paper period validates.
