import pandas as pd
import numpy as np
from src.strategy import momentum_scores, regime_on


def test_momentum_ranks_winners():
    idx = pd.date_range("2020-01-01", periods=200, freq="B")
    strong = pd.Series(np.linspace(100, 200, len(idx)), index=idx)
    weak = pd.Series(np.linspace(100, 80, len(idx)), index=idx)
    px = pd.DataFrame({"WIN": strong, "LOSE": weak})
    scores = momentum_scores(px, idx[-1])
    assert scores.index[0] == "WIN"


def test_regime_off_in_downtrend():
    idx = pd.date_range("2020-01-01", periods=250, freq="B")
    spy = pd.Series(np.linspace(200, 100, len(idx)), index=idx)
    assert regime_on(spy, idx[-1]) is False
