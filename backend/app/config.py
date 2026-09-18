"""KAVACH AI - Central configuration.

All settings are environment-driven with safe offline defaults. This module is
import-safe (no heavy deps) so the app can start with only the core packages.
"""
from __future__ import annotations

import os
from pathlib import Path

# --- Version / identity --------------------------------------------------------
VERSION = "1.0.0-prototype"
APP_NAME = "KAVACH AI"
APP_TAGLINE = "Sovereign On-Premise Agentic AI Workbench"

# --- Paths --------------------------------------------------------------------
# backend/app/config.py -> backend/app -> backend -> repo root (26117)
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

DEMO_DATA_DIR = Path(os.getenv("KAVACH_DEMO_DATA", str(REPO_ROOT / "demo-data")))
UPLOADS_DIR = Path(os.getenv("KAVACH_UPLOADS", str(DEMO_DATA_DIR / "uploads")))
GENERATED_DIR = Path(os.getenv("KAVACH_GENERATED", str(REPO_ROOT / "generated")))
DB_PATH = Path(os.getenv("KAVACH_DB", str(BACKEND_DIR / "kavach.db")))

# --- Security / mode ----------------------------------------------------------
KAVACH_MODE = os.getenv("KAVACH_MODE", "airgapped").strip().lower()
IS_AIRGAPPED = KAVACH_MODE == "airgapped"

# File-upload policy
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt", "docx", "csv", "py"}
MAX_UPLOAD_BYTES = int(os.getenv("KAVACH_MAX_UPLOAD_MB", "25")) * 1024 * 1024

# CORS
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Providers that are considered "external" and thus blocked in airgapped mode.
EXTERNAL_PROVIDERS = {"openai", "anthropic", "gemini", "google", "azure", "cohere", "bedrock"}


def ensure_dirs() -> None:
    """Create all runtime directories (idempotent)."""
    for d in (DEMO_DATA_DIR, UPLOADS_DIR, GENERATED_DIR):
        d.mkdir(parents=True, exist_ok=True)
