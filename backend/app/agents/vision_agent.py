"""Vision agent - detects equipment regions in the P&ID schematic.

Uses the multimodal 'Vision Model' route. For the offline prototype it returns
deterministic bounding-box regions for the known equipment tags.
"""
from __future__ import annotations

from ..services import scenario
from .base import BaseAgent, RunContext


class VisionAgent(BaseAgent):
    name = "vision_agent"

    def run(self, ctx: RunContext) -> RunContext:
        if ctx.artifacts.get("document"):
            # The canned regions describe the demo P&ID only; never attribute
            # them to a user's file.
            ctx.add_step(self.name, "Vision analysis skipped", status="skipped",
                         detail="No local vision model is loaded in the prototype; "
                                "uploaded documents are analysed from extracted text only.")
            return ctx
        # Deterministic pseudo-regions for each equipment item on the P&ID.
        regions = []
        for i, eq in enumerate(scenario.EQUIPMENT):
            regions.append({
                "equipment_id": eq["id"],
                "type": eq["type"],
                "bbox": [60 + i * 150, 120, 130, 90],
                "confidence": round(0.9 + (i % 3) * 0.02, 2),
            })
        ctx.artifacts["pid_regions"] = regions
        ctx.add_step(self.name, "P&ID regions detected",
                     detail=f"Detected {len(regions)} equipment regions: "
                            + ", ".join(r["equipment_id"] for r in regions))
        return ctx
