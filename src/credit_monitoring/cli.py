"""Comandos de execução a partir da raiz do repositório."""

import argparse
import json
from pathlib import Path

from credit_monitoring.data import audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["audit", "train"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    config = json.loads((root / "configs/pipeline.json").read_text(encoding="utf-8"))
    if args.command == "audit":
        result = audit(root, config)
        print(
            json.dumps({k: result[k] for k in ["rows_raw", "rows_usable", "partitions"]}, indent=2)
        )
    else:
        from credit_monitoring.model import train

        _, report = train(root, config)
        print(json.dumps(report["model"], indent=2))


if __name__ == "__main__":
    main()
