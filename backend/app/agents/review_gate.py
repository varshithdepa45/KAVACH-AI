"""Human-approval gate for agentic runs.

A finding must be approved by a human when it is high-risk, unsupported by
evidence from the local knowledge base, low-confidence, or was never verified.
The gate only ever *adds* review requirements; it never clears one.
"""
from __future__ import annotations

from .. import config
from ..services import knowledge as knowledge_service


def known_sources() -> set[str]:
    return {s["name"].lower() for s in knowledge_service.get_kb().stats()["sources"]}


def review_reasons(finding: dict, sources: set[str], *, verified: bool = True) -> list[str]:
    """Return why ``finding`` needs human approval (empty list = no approval needed)."""
    reasons: list[str] = []
    severity = str(finding.get("severity", "")).lower()
    if severity in config.HIGH_RISK_SEVERITIES:
        reasons.append(f"high-risk severity '{severity}'")

    evidence = finding.get("evidence") or []
    if not evidence:
        reasons.append("unsupported: no evidence cited")
    else:
        unknown = sorted({str(e.get("source", "")) for e in evidence
                          if str(e.get("source", "")).lower() not in sources})
        if unknown:
            reasons.append("unsupported: evidence source not in knowledge base "
                           f"({', '.join(unknown)})")

    try:
        confidence = float(finding.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < config.REVIEW_MIN_CONFIDENCE:
        reasons.append(f"low confidence ({confidence:g}% < {config.REVIEW_MIN_CONFIDENCE:g}%)")

    if not verified:
        reasons.append("not verified")
    if finding.get("needs_review") and not reasons:
        reasons.append("flagged for review by reasoning agent")
    return reasons


def apply(findings: list[dict], *, verified: bool = True) -> list[dict]:
    """Mark findings that need approval in place; return a summary of those findings."""
    sources = known_sources()
    required: list[dict] = []
    for f in findings:
        reasons = review_reasons(f, sources, verified=verified)
        if reasons:
            f["needs_review"] = 1
            f["review_reasons"] = reasons
            required.append({"title": f.get("title", ""), "severity": f.get("severity", ""),
                             "reasons": reasons})
    return required
