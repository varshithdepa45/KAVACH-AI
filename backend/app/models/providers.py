"""Model-provider abstraction for KAVACH AI.

Defines a clean ``BaseModelProvider`` interface and three adapters:

* ``MockLocalModelProvider`` - fully offline, deterministic inference used for
  the prototype. Produces stable, seed-based responses so demos are repeatable.
* ``OllamaProvider`` - stub adapter for a local Ollama runtime (http://localhost:11434).
  It is *local* infrastructure, not a cloud API, but is left unimplemented for the
  offline prototype and raises a clear error if invoked.
* ``VLLMProvider`` - stub adapter for a local vLLM OpenAI-compatible server.

All providers advertise ``is_external`` so the airgapped security guard can decide
whether they are permitted. Only cloud providers are considered external.
"""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationResult:
    text: str
    model: str
    provider: str
    tokens: int
    latency_ms: int
    meta: dict[str, Any] = field(default_factory=dict)


class BaseModelProvider(ABC):
    """Abstract interface every model backend implements."""

    name: str = "base"
    #: True only for cloud services; blocked in airgapped mode.
    is_external: bool = False

    @abstractmethod
    def generate(self, prompt: str, *, model: str, **kwargs: Any) -> GenerationResult:
        ...

    @abstractmethod
    def embed(self, text: str, *, model: str = "local-embed") -> list[float]:
        ...

    @abstractmethod
    def health(self) -> dict[str, Any]:
        ...


def _seed_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


class MockLocalModelProvider(BaseModelProvider):
    """Deterministic, offline provider.

    Responses are derived from a hash of the prompt so the same input always
    yields the same output - ideal for a reproducible hackathon demo. No network,
    no GPU, no external models are touched.
    """

    name = "mock-local"
    is_external = False

    def generate(self, prompt: str, *, model: str = "Qwen3-4B", **kwargs: Any) -> GenerationResult:
        seed = _seed_int(prompt + model)
        # Deterministic pseudo latency/token counts for realism.
        latency = 40 + (seed % 260)
        tokens = 48 + (seed % 400)
        text = (
            f"[{model} @ local] Deterministic analysis for prompt of "
            f"{len(prompt)} chars. Conclusion reference #{seed % 100000:05d}."
        )
        return GenerationResult(
            text=text,
            model=model,
            provider=self.name,
            tokens=tokens,
            latency_ms=latency,
            meta={"deterministic": True, "seed": seed % 100000},
        )

    def embed(self, text: str, *, model: str = "local-embed") -> list[float]:
        # Delegate to the RAG hash-embedding so embeddings are consistent app-wide.
        from ..rag.pipeline import hash_embedding

        return hash_embedding(text)

    def health(self) -> dict[str, Any]:
        return {"provider": self.name, "status": "online", "external": False}


class OllamaProvider(BaseModelProvider):
    """Stub adapter for a local Ollama server.

    Ollama runs models locally (not a cloud API), so it is NOT flagged external.
    For the offline prototype it is intentionally not wired to the network; calling
    ``generate`` raises ``NotImplementedError`` with guidance.
    """

    name = "ollama"
    is_external = False

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url

    def generate(self, prompt: str, *, model: str = "qwen3:4b", **kwargs: Any) -> GenerationResult:
        raise NotImplementedError(
            "OllamaProvider is a stub in the prototype. Start Ollama locally and "
            "implement HTTP calls to /api/generate to enable it."
        )

    def embed(self, text: str, *, model: str = "nomic-embed-text") -> list[float]:
        raise NotImplementedError("OllamaProvider.embed is a stub in the prototype.")

    def health(self) -> dict[str, Any]:
        return {"provider": self.name, "status": "offline-stub", "external": False,
                "base_url": self.base_url}


class VLLMProvider(BaseModelProvider):
    """Stub adapter for a local vLLM OpenAI-compatible server."""

    name = "vllm"
    is_external = False

    def __init__(self, base_url: str = "http://localhost:8001/v1") -> None:
        self.base_url = base_url

    def generate(self, prompt: str, *, model: str = "Qwen3-4B", **kwargs: Any) -> GenerationResult:
        raise NotImplementedError(
            "VLLMProvider is a stub in the prototype. Point base_url at a running "
            "vLLM server and implement the /v1/completions call to enable it."
        )

    def embed(self, text: str, *, model: str = "local-embed") -> list[float]:
        raise NotImplementedError("VLLMProvider.embed is a stub in the prototype.")

    def health(self) -> dict[str, Any]:
        return {"provider": self.name, "status": "offline-stub", "external": False,
                "base_url": self.base_url}


# Registry -------------------------------------------------------------------
_PROVIDERS: dict[str, BaseModelProvider] = {
    "mock-local": MockLocalModelProvider(),
    "ollama": OllamaProvider(),
    "vllm": VLLMProvider(),
}

#: The active provider for the prototype.
DEFAULT_PROVIDER = "mock-local"


def get_provider(name: str | None = None) -> BaseModelProvider:
    return _PROVIDERS[name or DEFAULT_PROVIDER]


def all_providers() -> dict[str, BaseModelProvider]:
    return dict(_PROVIDERS)
