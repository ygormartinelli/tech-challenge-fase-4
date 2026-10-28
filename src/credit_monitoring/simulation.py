"""Intervenções controladas; rótulos reais nunca são sobrescritos."""

import numpy as np

from credit_monitoring.data import TARGET


def scenarios(production, reference, config):
    features = production.drop(columns=TARGET)
    yield "control", features.copy(), {"kind": "observed", "target": production[TARGET].to_numpy()}
    invalid = features.copy()
    invalid.loc[invalid.index[0], "age"] = 12
    invalid.loc[invalid.index[1], "limit_bal"] = -1
    invalid.loc[invalid.index[2], "id"] = invalid.iloc[3].id
    yield "invalid", invalid, {"kind": "contract_violation"}
    for name, intensity in [("drift_moderate", 0.5), ("drift_severe", 1.0)]:
        batch = features.copy()
        credit_factor = 1 + intensity * (config["drift_limit_multiplier"] - 1)
        payment_factor = 1 + intensity * (config["drift_payment_multiplier"] - 1)
        batch["limit_bal"] = (batch.limit_bal * credit_factor).round().astype("int64")
        batch["pay_amt_1"] = (batch.pay_amt_1 * payment_factor).round().astype("int64")
        yield (
            name,
            batch,
            {
                "kind": "covariate_shift",
                "credit_factor": credit_factor,
                "payment_factor": payment_factor,
                "target_note": "Sem alvo contrafactual observado; acurácia não avaliada.",
            },
        )
    # P'(y=1|x) = q(x) + (1-2q(x))*P(y=1|x), com q conhecido no experimento.
    eligible = (features.pay_0 <= 0) & (features.bill_amt_1 > reference.bill_amt_1.median())
    rng = np.random.default_rng(config["seed"])
    flip = eligible.to_numpy() & (rng.random(len(features)) < config["concept_flip_probability"])
    synthetic = production[TARGET].to_numpy().copy()
    synthetic[flip] = 1 - synthetic[flip]
    yield (
        "concept_synthetic",
        features.copy(),
        {
            "kind": "synthetic_conditional_target_shift",
            "target": synthetic,
            "synthetic": True,
            "flipped_labels": int(flip.sum()),
            "eligible_rows": int(eligible.sum()),
            "probability": config["concept_flip_probability"],
            "bill_threshold_reference": float(reference.bill_amt_1.median()),
            "mechanism": "Inverter rótulo com probabilidade q nos perfis pay_0<=0 e "
            "bill_amt_1 acima da mediana da referência. X idêntico ao controle.",
        },
    )
