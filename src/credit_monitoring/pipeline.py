"""Demonstração por lotes, bloqueio de ingestão e rastreamento local."""

import os
import subprocess
import uuid
from html import escape
from importlib.metadata import version

import mlflow
import pandas as pd

from credit_monitoring.contracts import ContractViolation, validate
from credit_monitoring.data import FEATURES, audit, sha256, write_json
from credit_monitoring.drift import detect
from credit_monitoring.model import evaluate, train
from credit_monitoring.simulation import scenarios
from credit_monitoring.telemetry import Telemetry


def process_batch(batch, model, reference, config, output, telemetry):
    """Contrato é obrigatório e antecede qualquer transformação ou inferência."""
    with telemetry.stage("ingestion", len(batch)):
        received = batch.copy()
    with telemetry.stage("validation", len(batch)):
        valid = validate(received)
    with telemetry.stage("transformation", len(batch)):
        transformed = model.named_steps["transform"].transform(valid[FEATURES])
    with telemetry.stage("inference", len(batch)):
        probability = model.named_steps["classifier"].predict_proba(transformed)[:, 1]
    with telemetry.stage("drift", len(batch)):
        drift = detect(reference, valid, config, output)
    return probability, drift


def dashboard(destination, results):
    rows = []
    for result in results:
        scenario = escape(result["scenario"])
        features = ", ".join(result.get("drift", {}).get("drifted_features", [])) or "—"
        metrics = result.get("performance", {})
        auc = metrics.get("roc_auc")
        auc_text = f"{auc:.3f}" if auc is not None else "Não avaliado"
        report = (
            f'<a href="{scenario}/evidently.html">Evidently</a>'
            if "drift" in result
            else "Bloqueado antes da inferência"
        )
        rows.append(
            f"<tr><td>{scenario}</td><td>{result['status']}</td>"
            f"<td>{result['received_rows']}</td><td>{result['accepted_rows']}</td>"
            f"<td>{result['alerts']}</td><td>{escape(features)}</td><td>{auc_text}</td>"
            f"<td>{report}</td></tr>"
        )
    html = '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
    html += '<meta name="viewport" content="width=device-width,initial-scale=1">'
    html += "<title>Monitoramento de crédito</title><style>"
    html += "body{font:16px system-ui;margin:40px;background:#f3f6fa;color:#16263d}"
    html += "table{border-collapse:collapse;background:white;width:100%}td,th{padding:14px;"
    html += "border-bottom:1px solid #ddd;text-align:left}a{color:#135fa3}h1{font-size:32px}"
    html += "</style><h1>Monitoramento de crédito</h1>"
    html += "<p>Execução acadêmica real sobre cenários simulados. Alerta de drift não prova "
    html += "perda de desempenho. Concept drift abaixo usa rótulos sintéticos identificados.</p>"
    html += "<table><thead><tr><th>Cenário</th><th>Status</th><th>Recebidos</th>"
    html += "<th>Aceitos</th><th>Alertas</th><th>Features com drift</th><th>ROC-AUC</th>"
    html += "<th>Evidência</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    html += "<h2>Interpretação e operação</h2><p>Lote inválido é rejeitado integralmente. "
    html += "PSI ≥ 0,2 dispara um alerta por feature; queda de ROC-AUC ≥ 0,1 em relação ao "
    html += "controle dispara um alerta de desempenho na simulação de concept drift. "
    html += "Dados manipulados não têm resultado contrafactual observado.</p>"
    html += "<p>Latências, CPU, memória e etapas estão em summary.json e no MLflow local. "
    html += "Os recursos medidos são do processo Python; não representam disponibilidade de um "
    html += 'serviço de produção.</p><a href="summary.json">Resumo e telemetria</a></html>'
    (destination / "index.html").write_text(html, encoding="utf-8")


def run(root, config):
    os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING", "false")
    mlflow.set_tracking_uri("sqlite:///" + (root / "mlflow.db").as_posix())
    experiment_name = "credit-monitoring"
    if mlflow.get_experiment_by_name(experiment_name) is None:
        mlflow.create_experiment(experiment_name, artifact_location=(root / "mlartifacts").as_uri())
    mlflow.set_experiment(experiment_name)
    execution_id = uuid.uuid4().hex[:12]
    output = root / "reports/generated" / execution_id
    output.mkdir(parents=True)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()
    )
    versions = {
        name: version(name) for name in ["pandas", "scikit-learn", "evidently", "pandera", "mlflow"]
    }
    with mlflow.start_run(run_name=f"pipeline-{execution_id}") as parent:
        mlflow.set_tags(
            {"git_commit": commit, "working_tree_dirty": str(dirty), "execution_id": execution_id}
        )
        mlflow.log_params(config)
        mlflow.log_dict(versions, "versions.json")
        telemetry = Telemetry(root, parent.info.run_id, "preparation")
        with telemetry.stage("audit", 0):
            audited = audit(root, config)
        with telemetry.stage("training", audited["partitions"]["reference"]["rows"]):
            model, training = train(root, config)
        mlflow.log_metrics(
            {
                f"validation_{k}": v
                for k, v in training["model"].items()
                if isinstance(v, (int, float))
            }
        )
        mlflow.log_artifact(str(root / "models/baseline.joblib"), "model")
        mlflow.log_dict(training, "training.json")
        mlflow.log_dict(audited, "audit.json")
        mlflow.log_dict(config, "config.json")
        reference = pd.read_csv(root / "data/processed/reference.csv")
        production = pd.read_csv(root / "data/processed/production.csv")
        results = []
        control_auc = None
        for name, batch, metadata in scenarios(production, reference, config):
            with mlflow.start_run(run_name=name, nested=True) as child:
                tracker = Telemetry(root, child.info.run_id, name)
                result = {
                    "scenario": name,
                    "run_id": child.info.run_id,
                    "received_rows": len(batch),
                    "accepted_rows": 0,
                    "rejected_rows": 0,
                    "alerts": 0,
                    "metadata": {k: v for k, v in metadata.items() if k != "target"},
                }
                mlflow.set_tags(
                    {
                        "scenario": name,
                        "model_sha256": training["model_sha256"],
                        "source_sha256": audited["source"]["archive_sha256"],
                    }
                )
                try:
                    probability, drift = process_batch(
                        batch, model, reference, config, output / name, tracker
                    )
                    result.update(status="success", accepted_rows=len(batch), drift=drift)
                    result["alerts"] = len(drift["drifted_features"])
                    mlflow.log_metrics(
                        {
                            "drifted_features_count": result["alerts"],
                            "drifted_features_share": result["alerts"] / len(FEATURES),
                            **{f"psi_{row['feature']}": row["psi"] for row in drift["features"]},
                        }
                    )
                    if "target" in metadata:
                        metrics = evaluate(
                            metadata["target"], probability, config["decision_threshold"]
                        )
                        result["performance"] = metrics
                        mlflow.log_metrics(
                            {
                                f"performance_{k}": v
                                for k, v in metrics.items()
                                if isinstance(v, (int, float))
                            }
                        )
                        if name == "control":
                            control_auc = metrics["roc_auc"]
                        else:
                            drop = control_auc - metrics["roc_auc"]
                            result["auc_drop_vs_control"] = drop
                            result["performance_alert"] = (
                                drop >= config["performance_drop_threshold"]
                            )
                            result["alerts"] += int(result["performance_alert"])
                    result["prediction_count"] = len(probability)
                    mlflow.log_artifacts(str(output / name), "drift")
                except ContractViolation as error:
                    result.update(
                        status="rejected",
                        rejected_rows=len(batch),
                        alerts=1,
                        rules=error.rules,
                        prediction_count=0,
                    )
                    mlflow.set_tag("contract_status", "rejected")
                finally:
                    result["stages"] = tracker.events
                # Identificadores explícitos evitam atribuir métricas ao run pai.
                client = mlflow.MlflowClient()
                for key in ["received_rows", "accepted_rows", "rejected_rows", "alerts"]:
                    client.log_metric(child.info.run_id, key, result[key])
                client.set_tag(child.info.run_id, "batch_status", result["status"])
                results.append(result)
            if result["status"] == "rejected":
                client.set_terminated(child.info.run_id, status="FAILED")
        summary = {
            "execution_id": execution_id,
            "run_id": parent.info.run_id,
            "git_commit": commit,
            "working_tree_dirty": dirty,
            "versions": versions,
            "config": config,
            "config_sha256": sha256(root / "configs/pipeline.json"),
            "model_sha256": training["model_sha256"],
            "results": results,
            "preparation_stages": telemetry.events,
        }
        write_json(output / "summary.json", summary)
        dashboard(output, results)
        mlflow.log_artifact(str(output / "summary.json"))
        mlflow.log_artifact(str(output / "index.html"))
        mlflow.log_metric("alerts_total", sum(r["alerts"] for r in results))
    write_json(
        root / "reports/generated/latest.json",
        {"execution_id": execution_id, "path": str(output.relative_to(root))},
    )
    return summary
