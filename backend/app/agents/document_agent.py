"""Document agent - loads demo documents and performs (mock) OCR.

Reads the fictional document set for the scenario, reports load and OCR steps.
No real OCR engine is invoked; text comes from the canonical scenario content.
"""
from __future__ import annotations

from ..services import scenario
from .base import BaseAgent, RunContext


class DocumentAgent(BaseAgent):
    name = "document_agent"

    def run(self, ctx: RunContext) -> RunContext:
        docs = [d["filename"] for d in scenario.DEMO_DOCUMENTS]
        ctx.artifacts["documents"] = docs
        ctx.add_step(self.name, "Documents loaded",
                     detail=f"Loaded {len(docs)} documents: {', '.join(docs)}")

        text_docs = [d for d in scenario.DEMO_DOCUMENTS if d["doc_type"] in
                     {"report", "manual", "calculation"}]
        ctx.add_step(self.name, "OCR completed",
                     detail=f"OCR extracted text from {len(text_docs)} PDF documents "
                            "(inspection report, manual, calculation).")
        return ctx
