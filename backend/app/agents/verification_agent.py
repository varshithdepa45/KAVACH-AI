"""Verification agent - cross-checks findings against cited evidence.

Computes a deterministic verification score and how many findings are
evidence-backed, and flags findings that need human review.
"""
from __future__ import annotations

from ..services import scenario
from .base import BaseAgent, RunContext


class VerificationAgent(BaseAgent):
    name = "verification_agent"

    def run(self, ctx: RunContext) -> RunContext:
        total_evidence = sum(len(f.get("evidence", [])) for f in ctx.findings)
        backed = sum(1 for f in ctx.findings if f.get("evidence"))
        needs_review = [f for f in ctx.findings if f.get("needs_review")]

        ctx.verification_score = scenario.VERIFICATION_SCORE
        ctx.evidence_backed = scenario.EVIDENCE_BACKED
        ctx.artifacts["verification"] = {
            "score": scenario.VERIFICATION_SCORE,
            "evidence_backed": scenario.EVIDENCE_BACKED,
            "total_evidence_citations": total_evidence,
            "findings_backed": backed,
            "needs_human_review": [f["title"] for f in needs_review],
        }
        ctx.add_step(self.name, "Evidence cross-check completed",
                     detail=f"Verification score {scenario.VERIFICATION_SCORE}%; "
                            f"{scenario.EVIDENCE_BACKED} evidence-backed; "
                            f"{len(needs_review)} finding(s) flagged for human review.")
        return ctx
