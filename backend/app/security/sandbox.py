"""Mock sandbox executor for KAVACH AI.

This deliberately does NOT execute any real code. It models an isolated,
network-denied sandbox and returns a deterministic ``ISOLATED`` verdict plus a
static analysis-style summary. In a production build this would front a gVisor /
firejail / container sandbox.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass
class SandboxResult:
    status: str
    exit_code: int
    isolation: str
    network: str
    summary: str
    fingerprint: str


class MockSandboxExecutor:
    """Pretend to run code in a fully isolated environment (no real exec)."""

    def run(self, code: str, *, language: str = "python") -> SandboxResult:
        fp = hashlib.sha256(code.encode("utf-8", "ignore")).hexdigest()[:16]
        return SandboxResult(
            status="ISOLATED",
            exit_code=0,
            isolation="ISOLATED",
            network="DENIED",
            summary=(
                f"Static-only review of {len(code)} bytes of {language}. "
                "No execution performed; sandbox is network-denied and read-only."
            ),
            fingerprint=fp,
        )
