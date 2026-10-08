"""Reasoning agent - synthesizes findings from documents, vision and knowledge.

For the demo scenario it emits the canonical, deterministic finding set defined
in the scenario, attaching evidence to each finding. For an uploaded document it
extracts findings from the document's own text (see ``document_analysis``).
"""
from __future__ import annotations

from ..models.providers import generate_with_fallback
from ..services import document_analysis, scenario
from . import review_gate
from .base import BaseAgent, RunContext


class ReasoningAgent(BaseAgent):
    name = "reasoning_agent"

    def run(self, ctx: RunContext) -> RunContext:
        uploaded = ctx.artifacts.get("document")
        if uploaded:
            return self._run_document(ctx, uploaded["filename"])

        # A real (deterministic by default) provider call, kept for architectural realism.
        generate_with_fallback("Synthesize inspection findings for Unit 4", model="Qwen3-4B")

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

    def _run_document(self, ctx: RunContext, filename: str) -> RunContext:
        findings = document_analysis.find_findings(
            ctx.artifacts.get("document_text", ""), filename)
        # Same approval rules as agentic runs; the cited source is the document itself.
        for f in findings:
            reasons = review_gate.review_reasons(f, {filename.lower()})
            if reasons:
                f["needs_review"] = 1
                f["review_reasons"] = reasons
        ctx.findings = findings
        ctx.evidence = [{**ev, "finding_title": f["title"]}
                        for f in findings for ev in f["evidence"]]
        ctx.add_step(self.name, "Findings generated",
                     detail=f"Extracted {len(findings)} finding(s) from {filename} by local "
                            "risk-term matching (no model inference).")
        return ctx
