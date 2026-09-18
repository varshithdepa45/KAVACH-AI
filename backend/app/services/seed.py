"""Database seeding for KAVACH AI.

Populates the models catalog and the demo documents metadata on startup. Idempotent:
seeding only runs when the relevant tables are empty. Document metadata reflects the
files produced by demo-data/generate_demo_data.py (or their .txt fallbacks).
"""
from __future__ import annotations

from datetime import datetime, timezone

from .. import config
from ..database import db
from . import scenario

MODELS = [
    {"name": "Qwen3-4B", "provider": "mock-local", "kind": "reasoning",
     "status": "online", "params": "4B", "vram_gb": 6.5,
     "routing_rule": "Default for reasoning/text analysis and report synthesis."},
    {"name": "Vision Model", "provider": "mock-local", "kind": "vision",
     "status": "online", "params": "7B-VL", "vram_gb": 9.0,
     "routing_rule": "Images, P&ID schematics, OCR and region detection."},
    {"name": "Code Model", "provider": "mock-local", "kind": "code",
     "status": "online", "params": "3B", "vram_gb": 5.0,
     "routing_rule": "Source-code review and vulnerability scanning."},
    {"name": "Small Fast Model", "provider": "mock-local", "kind": "classification",
     "status": "online", "params": "0.5B", "vram_gb": 1.2,
     "routing_rule": "Fast classification, triage and lightweight extraction."},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_models() -> None:
    if db.count("models") > 0:
        return
    for m in MODELS:
        db.insert("models", m)


def seed_documents() -> None:
    if db.count("documents") > 0:
        return
    for d in scenario.DEMO_DOCUMENTS:
        # Determine actual path (file may be the pdf/png OR the .txt fallback).
        primary = config.DEMO_DATA_DIR / d["filename"]
        fallback = primary.with_suffix(".txt")
        if primary.exists():
            path, size = primary, primary.stat().st_size
        elif fallback.exists():
            path, size = fallback, fallback.stat().st_size
        else:
            path, size = primary, 0
        db.insert("documents", {
            "name": d["name"],
            "filename": path.name,
            "path": str(path),
            "doc_type": d["doc_type"],
            "size_bytes": size,
            "pages": d["pages"],
            "status": "ready",
            "summary": d["summary"],
            "created_at": _now(),
        })


def seed_all() -> None:
    seed_models()
    seed_documents()
    # Warm the knowledge base so /api/knowledge is populated immediately.
    from . import knowledge
    knowledge.get_kb()
