# VECTOR-2 Backtest Report (v1.3)

## What changed vs v1.2
- Sector concentration: max 3 names per sector and ≤30% weight per sector
- Liquidity filter: 20-day ADV ≥ $50,000,000
- Vol targeting available via env `TARGET_ANNUAL_VOL` (default **off** — on tests it reduced CAGR)

## Results

| Period | CAGR | MaxDD | Sharpe | SPY CAGR | Excess |
|--------|------|-------|--------|----------|--------|
| All | 17.0% | -30.1% | 0.90 | 15.0% | +2.0% |
| Train ≤2021 | 17.9% | -30.1% | 0.88 | 17.6% | +0.3% |
| Test ≥2022 | 15.3% | -23.6% | 0.91 | 11.5% | +3.7% |

Last holdings: INTC, AMD, CAT, GOOGL, FDX, CSCO, JNJ, C, MRK, CVS
