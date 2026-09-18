"""Router agent - classifies the task and selects the local model.

Delegates to the deterministic model router and records the routing decision,
then performs lightweight planning (the plan is fixed for the demo scenario).
"""
from __future__ import annotations

from ..models.router import route
from .base import BaseAgent, RunContext


class RouterAgent(BaseAgent):
    name = "router_agent"

    def run(self, ctx: RunContext) -> RunContext:
        decision = route(ctx.task_text or "inspect P&ID and inspection report for corrosion")
        ctx.routing = {
            "task_type": decision.task_type,
            "model": decision.model,
            "reason": decision.reason,
            "confidence": decision.confidence,
        }
        ctx.add_step(
            self.name,
            f"Task routed to {decision.model}",
            detail=f"task_type={decision.task_type}; {decision.reason}",
        )
        # Planner sub-step (fixed multi-step plan for the scenario).
        plan = [
            "Load and OCR documents",
            "Detect P&ID equipment regions",
            "Retrieve knowledge for detected equipment",
            "Reason over evidence to generate findings",
            "Cross-check evidence and verify",
            "Generate deliverable report",
        ]
        ctx.artifacts["plan"] = plan
        ctx.add_step(self.name, "Execution plan created",
                     detail="; ".join(f"{i+1}. {p}" for i, p in enumerate(plan)))
        return ctx
