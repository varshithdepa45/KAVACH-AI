"""System-status service for KAVACH AI.

Returns a deterministic-ish snapshot of the (mock) local infrastructure with a
small time-seeded jitter so the dashboard feels alive while staying reproducible
within a short window.
"""
from __future__ import annotations

import time

from .. import config
from ..database import db
from ..rag.pipeline import backend_info
from ..security.sandbox import MockSandboxExecutor


def _jitter(base: float, spread: float) -> float:
    # Deterministic within a ~5s bucket; small variation over time.
    bucket = int(time.time() // 5)
    val = base + ((bucket * 2654435761) % 1000) / 1000.0 * spread - spread / 2
    return round(max(0.0, val), 1)


def snapshot() -> dict:
    models = db.fetch_all("SELECT name, status FROM models")
    online = sum(1 for m in models if m["status"] == "online")
    sandbox = MockSandboxExecutor().run("print('healthcheck')")
    return {
        "mode": config.KAVACH_MODE,
        "network": "airgapped (outbound blocked)" if config.IS_AIRGAPPED else "open",
        "gpu": {
            "utilization_pct": _jitter(58, 20),
            "memory_used_pct": _jitter(64, 16),
            "temperature_c": _jitter(61, 8),
            "device": "Local GPU (mock)",
        },
        "models": {
            "online": online,
            "total": len(models),
            "list": models,
        },
        "vector_db": {
            "status": "online",
            "backend": backend_info()["vector_backend"],
        },
        "ocr": {"status": "online", "engine": "mock-ocr"},
        "sandbox": {"status": sandbox.status, "network": sandbox.network},
        "documents": db.count("documents"),
        "runs": db.count("agent_runs"),
    }
