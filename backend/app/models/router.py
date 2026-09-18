"""Deterministic model router for KAVACH AI.

Maps free-text task descriptions to a ``task_type`` and selects the most
appropriate local model, returning a human-readable reason. The classification is
keyword-driven and fully deterministic (no ML at inference time) so demos are
reproducible.

Model catalog:
    * Qwen3-4B            - general reasoning / text
    * Vision Model        - images, P&ID, schematics, OCR regions
    * Code Model          - source code analysis
    * Small Fast Model    - classification / lightweight extraction
"""
from __future__ import annotations

from dataclasses import dataclass

# task_type -> model name
_TYPE_TO_MODEL = {
    "vision": "Vision Model",
    "code": "Code Model",
    "classification": "Small Fast Model",
    "extraction": "Small Fast Model",
    "reasoning": "Qwen3-4B",
}

# Keyword signals for classification (checked in priority order).
_SIGNALS: list[tuple[str, tuple[str, ...]]] = [
    ("vision", ("p&id", "pid", "image", "png", "jpg", "jpeg", "schematic",
                "diagram", "drawing", "ocr", "photo", "scan", "vision")),
    ("code", ("code", ".py", "python", "script", "function", "vulnerab",
              "sast", "lint", "repository", "source")),
    ("extraction", ("extract", "parse", "field", "table", "form", "csv",
                    "metadata")),
    ("classification", ("classify", "categor", "label", "tag", "triage",
                        "route")),
]


@dataclass
class RoutingDecision:
    task_type: str
    model: str
    reason: str
    confidence: float


def classify(task_text: str) -> str:
    """Return a deterministic task_type for the given text."""
    text = (task_text or "").lower()
    for task_type, keywords in _SIGNALS:
        if any(k in text for k in keywords):
            return task_type
    return "reasoning"


def route(task_text: str) -> RoutingDecision:
    """Classify the task and select the target model with a reason string."""
    task_type = classify(task_text)
    model = _TYPE_TO_MODEL.get(task_type, "Qwen3-4B")
    reasons = {
        "vision": "Detected visual/P&ID content; routing to the multimodal Vision Model.",
        "code": "Detected source-code analysis intent; routing to the Code Model.",
        "extraction": "Detected structured extraction intent; routing to the Small Fast Model.",
        "classification": "Detected classification/triage intent; routing to the Small Fast Model.",
        "reasoning": "General analytical task; routing to Qwen3-4B for reasoning.",
    }
    # Deterministic confidence banding by type.
    confidence = {
        "vision": 0.93, "code": 0.9, "extraction": 0.88,
        "classification": 0.86, "reasoning": 0.91,
    }[task_type]
    return RoutingDecision(
        task_type=task_type,
        model=model,
        reason=reasons[task_type],
        confidence=confidence,
    )


def routing_rules() -> list[dict]:
    """Static description of routing rules for the /api/models endpoint."""
    return [
        {"task_type": "reasoning", "model": "Qwen3-4B",
         "when": "General text analysis, findings, report reasoning"},
        {"task_type": "vision", "model": "Vision Model",
         "when": "Images, P&ID schematics, OCR, region detection"},
        {"task_type": "code", "model": "Code Model",
         "when": "Source-code review and vulnerability scanning"},
        {"task_type": "extraction", "model": "Small Fast Model",
         "when": "Field/table extraction from documents"},
        {"task_type": "classification", "model": "Small Fast Model",
         "when": "Fast classification and task triage"},
    ]
