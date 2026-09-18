"""Knowledge agent - retrieves supporting context from the RAG knowledge base.

Queries the deterministic in-memory vector index for each detected equipment tag
and stores the retrieved chunks for the reasoning agent.
"""
from __future__ import annotations

from ..services import knowledge as knowledge_service
from .base import BaseAgent, RunContext


class KnowledgeAgent(BaseAgent):
    name = "knowledge_agent"

    def run(self, ctx: RunContext) -> RunContext:
        kb = knowledge_service.get_kb()
        queries = ["corrosion P-101 outlet wall thickness",
                   "control valve V-204 actuator packing",
                   "HX-301 fouling factor"]
        retrieved = []
        for q in queries:
            hits = kb.search(q, top_k=2)
            retrieved.extend(hits)
        ctx.artifacts["retrieved"] = retrieved
        ctx.add_step(self.name, "Knowledge retrieved",
                     detail=f"Retrieved {len(retrieved)} chunks across "
                            f"{len(queries)} equipment queries from the local vector DB.")
        return ctx
