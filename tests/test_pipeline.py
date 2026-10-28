import json
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from credit_monitoring.contracts import ContractViolation, validate
from credit_monitoring.data import FEATURES, prepare
from credit_monitoring.drift import detect
from credit_monitoring.pipeline import process_batch
from credit_monitoring.simulation import scenarios
from credit_monitoring.telemetry import Telemetry

CONFIG = json.loads((Path(__file__).parents[1] / "configs/pipeline.json").read_text())


def test_invalid_batch_never_reaches_model(valid_batch, monkeypatch, tmp_path):
    monkeypatch.setattr("mlflow.log_metrics", lambda metrics: None)
    telemetry = Telemetry(tmp_path, "test-run", "invalid")
    model = Mock()
    valid_batch.loc[0, "age"] = 12
    with pytest.raises(ContractViolation):
        process_batch(valid_batch, model, valid_batch, CONFIG, tmp_path / "result", telemetry)
    assert not model.mock_calls
    assert [event["stage"] for event in telemetry.events] == ["ingestion", "validation"]
    assert telemetry.events[-1]["status"] == "failed"
    assert not (tmp_path / "result").exists()
    log = (tmp_path / "logs/pipeline.jsonl").read_text()
    assert '"run_id": "test-run"' in log
    assert "limit_bal" not in log


def test_synthetic_concept_preserves_features_and_original_labels(valid_batch):
    production = valid_batch.assign(default=np.arange(len(valid_batch)) % 2)
    production["bill_amt_1"] = np.arange(len(production)) * 100
    original = production.copy(deep=True)
    result = {
        name: (batch, metadata)
        for name, batch, metadata in scenarios(production, production, CONFIG)
    }
    pd.testing.assert_frame_equal(production, original)
    pd.testing.assert_frame_equal(result["control"][0], result["concept_synthetic"][0])
    assert result["concept_synthetic"][1]["synthetic"]
    assert result["concept_synthetic"][1]["flipped_labels"] > 0
    for name in ["control", "drift_moderate", "drift_severe", "concept_synthetic"]:
        validate(result[name][0])
    with pytest.raises(ContractViolation):
        validate(result["invalid"][0])
    second = list(scenarios(production, production, CONFIG))[-1][2]["target"]
    np.testing.assert_array_equal(result["concept_synthetic"][1]["target"], second)


def test_partition_excludes_all_duplicate_profiles_and_is_reproducible(valid_batch):
    frame = pd.concat([valid_batch] * 300, ignore_index=True)
    frame["id"] = np.arange(1, len(frame) + 1)
    frame["limit_bal"] = frame.id * 10
    frame["default"] = frame.id % 2
    frame.loc[1, "limit_bal"] = frame.loc[0, "limit_bal"]
    splits, removed = prepare(frame, 42, 0.2, 0.2)
    assert removed.sum() == 2
    assert sum(map(len, splits.values())) == len(frame) - 2
    hashes = [set(pd.util.hash_pandas_object(f[FEATURES], index=False)) for f in splits.values()]
    for i, left in enumerate(hashes):
        for right in hashes[i + 1 :]:
            assert left.isdisjoint(right)
    again, _ = prepare(frame, 42, 0.2, 0.2)
    for key in splits:
        pd.testing.assert_frame_equal(splits[key], again[key])


@pytest.mark.integration
def test_evidently_detects_known_shift_and_identical_control(valid_batch, tmp_path):
    reference = pd.concat([valid_batch] * 20, ignore_index=True)
    reference["id"] = np.arange(1, len(reference) + 1)
    reference["limit_bal"] = np.arange(1, len(reference) + 1) * 100
    reference["pay_0"] = np.arange(len(reference)) % 3 - 1
    control = detect(reference, reference.copy(), CONFIG, tmp_path / "control")
    assert control["drifted_features"] == []
    shifted = reference.copy()
    shifted["limit_bal"] *= 100
    shifted["pay_0"] += 3
    result = detect(reference, shifted, CONFIG, tmp_path / "shifted")
    assert {"limit_bal", "pay_0"}.issubset(result["drifted_features"])
    assert (tmp_path / "shifted/evidently.html").stat().st_size > 1000
