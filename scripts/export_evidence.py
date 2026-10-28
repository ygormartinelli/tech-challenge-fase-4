"""Publica somente artefatos agregados permitidos, nunca dados ou modelos."""

import argparse
import json
import re
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, default=Path.cwd())
parser.add_argument("--destination", type=Path, default=Path("reports/evidence"))
args = parser.parse_args()
source = args.source.resolve()
destination = args.destination.resolve()
latest = json.loads((source / "reports/generated/latest.json").read_text(encoding="utf-8"))
execution = source / "reports/generated" / latest["execution_id"]
destination.mkdir(parents=True, exist_ok=True)
for origin, target in [
    (execution / "summary.json", destination / "summary.json"),
    (source / "reports/generated/training.json", destination / "training.json"),
    (source / "reports/generated/audit/audit.json", destination / "audit.json"),
    (execution / "drift_severe/evidently.html", destination / "drift_severe/evidently.html"),
]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origin, target)
    if target.suffix == ".html":
        content = target.read_text(encoding="utf-8")
        target.write_text(re.sub(r"(?m)^[\t ]+$", "", content), encoding="utf-8")
html = (execution / "index.html").read_text(encoding="utf-8")
for scenario in ["control", "drift_moderate", "concept_synthetic"]:
    html = html.replace(
        f'<a href="{scenario}/evidently.html">Evidently</a>',
        '<a href="summary.json">Resumo JSON</a>',
    )
(destination / "index.html").write_text(html, encoding="utf-8")
print(f"Evidências agregadas da execução {latest['execution_id']} exportadas.")
