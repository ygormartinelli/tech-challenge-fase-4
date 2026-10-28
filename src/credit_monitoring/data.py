"""Aquisição, auditoria e partições sem sobreposição de perfis financeiros."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd
from sklearn.model_selection import train_test_split

TARGET = "default"
FEATURES = ["limit_bal"] + [f"pay_{i}" for i in [0, 2, 3, 4, 5, 6]] + [
    f"{prefix}_{i}" for prefix in ["bill_amt", "pay_amt"] for i in range(1, 7)
]
DEMOGRAPHICS = ["sex", "education", "marriage", "age"]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def acquire(root: Path, config: dict) -> Path:
    """Preserva o ZIP original; extração restrita ao XLS esperado."""
    folder = root / "data/raw"
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / "uci_credit.zip"
    if not archive.exists():
        with urlopen(config["source_url"], timeout=120) as response:
            payload = response.read()
        temporary = archive.with_suffix(".download")
        temporary.write_bytes(payload)
        with ZipFile(temporary) as zipped:
            if len([n for n in zipped.namelist() if n.endswith(".xls")]) != 1:
                raise ValueError("Fonte não contém exatamente um XLS")
        temporary.replace(archive)
    destination = folder / "credit.xls"
    with ZipFile(archive) as zipped:
        names = [n for n in zipped.namelist() if n.endswith(".xls")]
        if len(names) != 1:
            raise ValueError("Arquivo de origem inesperado")
        destination.write_bytes(zipped.read(names[0]))
    metadata_path = folder / "source.json"
    if not metadata_path.exists():
        write_json(metadata_path, {
            "url": config["source_url"], "downloaded_at": datetime.now(UTC).isoformat(),
            "archive_sha256": sha256(archive), "xls_sha256": sha256(destination),
            "license": "CC BY 4.0", "doi": "10.24432/C55S3H",
        })
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata["archive_sha256"] != sha256(archive):
        raise ValueError("Checksum da fonte mudou; revisar antes de continuar")
    return destination


def read_source(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, header=1)
    frame.columns = [str(c).lower().replace("default payment next month", TARGET) for c in frame]
    expected = {"id", TARGET, *FEATURES, *DEMOGRAPHICS}
    if set(frame) != expected:
        raise ValueError("Colunas da fonte divergem do dicionário esperado")
    return frame


def prepare(frame: pd.DataFrame, seed: int, validation: float, production: float):
    """Exclui todos os perfis financeiros repetidos antes de separar por cliente."""
    if frame.isna().any().any() or not frame.id.is_unique:
        raise ValueError("Fonte com nulos ou IDs repetidos: revisar a auditoria")
    if not set(frame[TARGET].unique()) == {0, 1}:
        raise ValueError("Alvo deve conter as duas classes binárias")
    duplicate_mask = frame.duplicated(FEATURES, keep=False)
    clean = frame.loc[~duplicate_mask].copy()
    if len(clean) < 5000:
        raise ValueError("Menos de 5.000 observações utilizáveis")
    reference, heldout = train_test_split(
        clean, test_size=validation + production, random_state=seed, stratify=clean[TARGET]
    )
    valid, current = train_test_split(
        heldout, test_size=production / (validation + production),
        random_state=seed, stratify=heldout[TARGET],
    )
    return {"reference": reference, "validation": valid, "production": current}, duplicate_mask


def audit(root: Path, config: dict) -> dict:
    frame = read_source(acquire(root, config))
    splits, duplicates = prepare(
        frame, config["seed"], config["validation_fraction"], config["production_fraction"]
    )
    processed = root / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)
    partitions = {}
    for name, subset in splits.items():
        path = processed / f"{name}.csv"
        subset.to_csv(path, index=False, lineterminator="\n")
        partitions[name] = {
            "rows": len(subset), "default_rate": float(subset[TARGET].mean()),
            "sha256": sha256(path),
        }
    summary = {
        "source": json.loads((root / "data/raw/source.json").read_text(encoding="utf-8")),
        "rows_raw": len(frame), "columns": len(frame.columns),
        "missing_cells": int(frame.isna().sum().sum()), "unique_ids": int(frame.id.nunique()),
        "exact_duplicates_without_id": int(frame.drop(columns="id").duplicated().sum()),
        "rows_excluded_repeated_financial_profile": int(duplicates.sum()),
        "rows_usable": int((~duplicates).sum()),
        "default_rate_raw": float(frame[TARGET].mean()),
        "categories": {c: sorted(int(x) for x in frame[c].unique()) for c in
                       ["sex", "education", "marriage", "pay_0"]},
        "negative_bill_counts": {c: int((frame[c] < 0).sum()) for c in FEATURES if "bill" in c},
        "numeric_summary": frame.drop(columns="id").describe().to_dict(),
        "target_correlations": frame[FEATURES + [TARGET]].corr()[TARGET].drop(TARGET).to_dict(),
        "partitions": partitions, "seed": config["seed"],
        "features": FEATURES, "excluded_from_model": ["id", TARGET, *DEMOGRAPHICS],
        "decision": "accepted_for_academic_simulation",
        "duplicate_policy": "Excluir todos os membros de perfis financeiros idênticos; "
                            "política conservadora que altera a população e deve ser reportada.",
    }
    output = root / "reports/generated/audit"
    write_json(output / "audit.json", summary)
    table = frame.drop(columns="id").describe().round(2).T.to_html()
    html = '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Auditoria UCI</title>'
    html += '<style>body{font:16px system-ui;max-width:1200px;margin:40px auto}td,th{padding:8px}</style>'
    html += f'<h1>Auditoria da base UCI</h1><p>{len(frame):,} registros originais; '
    html += f'{summary["rows_usable"]:,} após exclusão conservadora de perfis repetidos.</p>'
    html += '<p>Dados históricos de Taiwan. Partições por cliente, sem cronologia real. '
    html += 'Limite de crédito não é renda; faturas negativas são preservadas.</p>' + table
    html += '<p>Consulte audit.json para origem, checksum, categorias e partições.</p></html>'
    (output / "audit.html").write_text(html, encoding="utf-8")
    return summary
