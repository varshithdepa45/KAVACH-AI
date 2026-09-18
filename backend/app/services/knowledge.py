"""Knowledge-base service - builds and holds the RAG index (singleton).

The index is populated from the canonical scenario knowledge texts at startup.
"""
from __future__ import annotations

from ..rag.pipeline import KnowledgeBase
from . import scenario

_KB: KnowledgeBase | None = None


def get_kb() -> KnowledgeBase:
    global _KB
    if _KB is None:
        _KB = KnowledgeBase()
        for source, text in scenario.KNOWLEDGE_TEXTS.items():
            _KB.add(text, source=source, page=1)
    return _KB


def stats() -> dict:
    kb = get_kb()
    s = kb.stats()
    s["sample_chunks"] = kb.sample_chunks(6)
    return s
