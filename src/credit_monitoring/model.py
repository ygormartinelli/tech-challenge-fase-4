"""Baseline financeiro simples, avaliação independente e métricas por grupo."""

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from credit_monitoring.contracts import validate
from credit_monitoring.data import FEATURES, TARGET, sha256, write_json


def signed_log(values):
    """Reduz assimetria monetária sem descartar créditos/faturas negativas."""
    return np.sign(values) * np.log1p(np.abs(values))


def build_model(config):
    status = [c for c in FEATURES if c.startswith("pay_") and not c.startswith("pay_amt")]
    monetary = [c for c in FEATURES if c not in status]
    transform = ColumnTransformer(
        [
            (
                "amounts",
                Pipeline([("log", FunctionTransformer(signed_log)), ("scale", StandardScaler())]),
                monetary,
            ),
            ("status", OneHotEncoder(handle_unknown="ignore"), status),
        ]
    )
    return Pipeline(
        [
            ("transform", transform),
            (
                "classifier",
                LogisticRegression(max_iter=config["max_iter"], random_state=config["seed"]),
            ),
        ]
    )


def evaluate(target, probability, threshold):
    prediction = np.asarray(probability) >= threshold
    both_classes = len(np.unique(target)) == 2
    return {
        "rows": len(target),
        "positive_rate": float(np.mean(target)),
        "roc_auc": float(roc_auc_score(target, probability)) if both_classes else None,
        "pr_auc": float(average_precision_score(target, probability)) if both_classes else None,
        "precision": float(precision_score(target, prediction, zero_division=0)),
        "recall": float(recall_score(target, prediction, zero_division=0)),
        "brier": float(brier_score_loss(target, probability)),
        "confusion_matrix": confusion_matrix(target, prediction, labels=[0, 1]).tolist(),
    }


def group_metrics(frame, probability, threshold):
    """Grupos de sexo e idade; métricas descritivas não certificam equidade."""
    result = {}
    groups = {
        "sex": frame.sex.astype(str),
        "age": pd.cut(frame.age, bins=[17, 29, 44, 120], labels=["18-29", "30-44", "45+"]),
    }
    for attribute, values in groups.items():
        for group in values.unique():
            mask = np.asarray(values == group)
            stats = evaluate(frame.loc[mask, TARGET], probability[mask], threshold)
            positives = int(frame.loc[mask, TARGET].sum())
            recall = stats["recall"]
            # Wilson para recall: intervalo binomial de verdadeiros positivos/positivos.
            if positives:
                z = 1.96
                denominator = 1 + z * z / positives
                center = (recall + z * z / (2 * positives)) / denominator
                radius = (
                    z
                    * np.sqrt(recall * (1 - recall) / positives + z * z / (4 * positives**2))
                    / denominator
                )
                stats["recall_ci95"] = [float(center - radius), float(center + radius)]
            stats["positive_count"] = positives
            result[f"{attribute}:{group}"] = stats
    return result


def train(root, config):
    reference = validate(pd.read_csv(root / "data/processed/reference.csv"), labeled=True)
    validation = validate(pd.read_csv(root / "data/processed/validation.csv"), labeled=True)
    model = build_model(config)
    model.fit(reference[FEATURES], reference[TARGET])
    probability = model.predict_proba(validation[FEATURES])[:, 1]
    dummy = DummyClassifier(strategy="prior").fit(reference[FEATURES], reference[TARGET])
    report = {
        "model": evaluate(validation[TARGET], probability, config["decision_threshold"]),
        "dummy": evaluate(
            validation[TARGET],
            dummy.predict_proba(validation[FEATURES])[:, 1],
            config["decision_threshold"],
        ),
        "groups": group_metrics(validation, probability, config["decision_threshold"]),
        "threshold": config["decision_threshold"],
        "seed": config["seed"],
        "features": FEATURES,
        "reference_sha256": sha256(root / "data/processed/reference.csv"),
        "validation_sha256": sha256(root / "data/processed/validation.csv"),
    }
    location = root / "models/baseline.joblib"
    location.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, location)
    reloaded = joblib.load(location)  # Somente artefato local produzido por esta execução.
    if not np.allclose(probability, reloaded.predict_proba(validation[FEATURES])[:, 1]):
        raise RuntimeError("Predições divergiram após recarregar o modelo")
    report["model_sha256"] = sha256(location)
    report["reload_predictions_match"] = True
    write_json(root / "reports/generated/training.json", report)
    return model, report
