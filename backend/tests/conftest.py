"""Test fixtures: isolated SQLite DB + generated dir, default airgapped/mock config."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="kavach-tests-"))
os.environ["KAVACH_DB"] = str(_TMP / "kavach.db")
os.environ["KAVACH_GENERATED"] = str(_TMP / "generated")
os.environ["KAVACH_UPLOADS"] = str(_TMP / "uploads")
os.environ["KAVACH_MODE"] = "airgapped"
os.environ.pop("KAVACH_INFERENCE_PROVIDER", None)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
