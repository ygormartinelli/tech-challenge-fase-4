"""Logs sanitizados e métricas de cada etapa, inclusive falhas."""

import json
import time
from contextlib import contextmanager
from datetime import UTC, datetime

import mlflow
import psutil


class Telemetry:
    def __init__(self, root, run_id, batch_id):
        self.path = root / "logs/pipeline.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.batch_id = batch_id
        self.events = []

    @contextmanager
    def stage(self, name, volume):
        start = time.perf_counter()
        cpu_start = time.process_time()
        state = "success"
        try:
            yield
        except Exception:
            state = "failed"
            raise
        finally:
            seconds = time.perf_counter() - start
            cpu_seconds = time.process_time() - cpu_start
            memory = psutil.Process().memory_info().rss / 1024**2
            event = {
                "time_utc": datetime.now(UTC).isoformat(),
                "run_id": self.run_id,
                "batch_id": self.batch_id,
                "stage": name,
                "status": state,
                "seconds": seconds,
                "input_rows": volume,
                "cpu_seconds": cpu_seconds,
                "rss_mb": memory,
            }
            self.events.append(event)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event) + "\n")
            mlflow.log_metrics(
                {
                    f"{name}_seconds": seconds,
                    f"{name}_success": int(state == "success"),
                    f"{name}_input_rows": volume,
                    f"{name}_cpu_seconds": cpu_seconds,
                    f"{name}_rss_mb": memory,
                }
            )
