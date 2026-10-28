"""Fixtures artificiais pequenas, exclusivas para testes de comportamento."""

import numpy as np
import pandas as pd
import pytest

from credit_monitoring.data import FEATURES


@pytest.fixture
def valid_batch():
    frame = pd.DataFrame({c: np.full(20, 100, dtype="int64") for c in FEATURES})
    for column in [c for c in FEATURES if c.startswith("pay_") and "amt" not in c]:
        frame[column] = 0
    frame["id"] = np.arange(1, 21)
    frame["age"] = 30
    frame["sex"] = 1
    frame["education"] = 2
    frame["marriage"] = 1
    return frame
