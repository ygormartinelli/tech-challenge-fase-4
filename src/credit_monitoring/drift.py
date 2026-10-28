"""Relatório Evidently com PSI e KS suplementar corrigido por Bonferroni."""

from evidently import Report
from evidently.presets import DataDriftPreset
from scipy.stats import ks_2samp

from credit_monitoring.data import FEATURES, write_json


def detect(reference, current, config, output):
    output.mkdir(parents=True, exist_ok=True)
    snapshot = Report(
        [DataDriftPreset(columns=FEATURES, method="psi", threshold=config["psi_threshold"])]
    ).run(current_data=current[FEATURES], reference_data=reference[FEATURES])
    snapshot.save_html(str(output / "evidently.html"))
    raw = snapshot.dict()
    rows = []
    for metric in raw["metrics"]:
        column = metric["config"].get("column")
        if column not in FEATURES:
            continue
        psi = float(metric["value"])
        ks = ks_2samp(reference[column], current[column], method="asymp")
        rows.append(
            {
                "feature": column,
                "psi": psi,
                "drift": psi >= config["psi_threshold"],
                "ks_statistic": float(ks.statistic),
                "ks_pvalue": float(ks.pvalue),
                "ks_significant_bonferroni": bool(ks.pvalue < config["ks_alpha"] / len(FEATURES)),
            }
        )
    if {r["feature"] for r in rows} != set(FEATURES):
        raise RuntimeError("Relatório Evidently não contém todas as features esperadas")
    result = {
        "reference_rows": len(reference),
        "current_rows": len(current),
        "method": "Evidently PSI",
        "threshold": config["psi_threshold"],
        "ks_family_alpha": config["ks_alpha"],
        "ks_comparisons": len(FEATURES),
        "features": rows,
        "drifted_features": [r["feature"] for r in rows if r["drift"]],
        "interpretation": "Alerta por feature via PSI; KS complementar. "
        "KS em variáveis discretas exige cautela. Nenhum teste prova causalidade.",
    }
    write_json(output / "drift.json", result)
    return result
