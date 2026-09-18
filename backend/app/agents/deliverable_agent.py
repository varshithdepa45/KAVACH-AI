"""Deliverable agent - generates the final report artifacts.

Delegates file writing to the deliverables service (which always writes .txt and
.md, and adds .docx/.xlsx/.pdf when the optional libraries are importable).
"""
from __future__ import annotations

from ..services import deliverables as deliverable_service
from .base import BaseAgent, RunContext


class DeliverableAgent(BaseAgent):
    name = "deliverable_agent"

    def run(self, ctx: RunContext) -> RunContext:
        produced = deliverable_service.generate_all(ctx)
        ctx.artifacts["deliverables"] = produced
        formats = ", ".join(sorted({d["fmt"] for d in produced}))
        ctx.add_step(self.name, "Report generated",
                     detail=f"Produced {len(produced)} deliverable file(s): {formats}.")
        return ctx
