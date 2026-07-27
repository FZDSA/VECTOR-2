import pandas as pd
import numpy as np
from src.strategy import momentum_scores, regime_on, select_portfolio


def test_momentum_ranks_winners():
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    strong = pd.Series(np.linspace(100, 200, len(idx)), index=idx)
    weak = pd.Series(np.linspace(100, 80, len(idx)), index=idx)
    px = pd.DataFrame({"WIN": strong, "LOSE": weak})
    scores = momentum_scores(px, idx[-1])
    assert scores.index[0] == "WIN"


def test_regime_off_in_downtrend():
    idx = pd.date_range("2020-01-01", periods=250, freq="B")
    spy = pd.Series(np.linspace(200, 100, len(idx)), index=idx)
    assert regime_on(spy, idx[-1]) is False


def test_select_returns_weights():
    idx = pd.date_range("2018-01-01", periods=400, freq="B")
    rng = np.random.default_rng(0)
    px = pd.DataFrame({
        "A": 100 * np.cumprod(1 + rng.normal(0.001, 0.01, len(idx))),
        "B": 100 * np.cumprod(1 + rng.normal(0.0005, 0.02, len(idx))),
        "BIL": 100 * np.cumprod(1 + np.full(len(idx), 0.00008)),
    }, index=idx)
    spy = pd.Series(100 * np.cumprod(1 + rng.normal(0.0007, 0.01, len(idx))), index=idx)
    w = select_portfolio(px, spy, idx[-1], safe_asset="BIL")
    assert isinstance(w, dict)
    if w:
        assert abs(sum(w.values()) - 1.0) < 1e-6
