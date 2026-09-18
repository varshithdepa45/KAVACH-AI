"""Reasoning agent - synthesizes findings from documents, vision and knowledge.

Runs on Qwen3-4B (local). For the prototype it emits the canonical, deterministic
finding set defined in the scenario, attaching evidence to each finding.
"""
from __future__ import annotations

from ..models.providers import get_provider
from ..services import scenario
from .base import BaseAgent, RunContext


class ReasoningAgent(BaseAgent):
    name = "reasoning_agent"

    def run(self, ctx: RunContext) -> RunContext:
        provider = get_provider()
        # A real (deterministic) provider call, kept for architectural realism.
        provider.generate("Synthesize inspection findings for Unit 4", model="Qwen3-4B")

        findings: list[dict] = []
        evidence: list[dict] = []
        for f in scenario.FINDINGS:
            finding = {
                "title": f["title"],
                "description": f["description"],
                "severity": f["severity"],
                "confidence": f["confidence"],
                "equipment_id": f["equipment_id"],
                "needs_review": f["needs_review"],
                "evidence": f["evidence"],
            }
            findings.append(finding)
            for ev in f["evidence"]:
                evidence.append({**ev, "finding_title": f["title"]})

        ctx.findings = findings
        ctx.evidence = evidence
        ctx.add_step(self.name, "Findings generated",
                     detail=f"Generated {len(findings)} findings with "
                            f"{len(evidence)} evidence citations.")
        return ctx
