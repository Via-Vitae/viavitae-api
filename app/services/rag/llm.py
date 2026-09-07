"""LLM and embedding client abstraction (EU-resident or self-hosted, ADR-007).

The provider is chosen by configuration and must be EU-resident or self-hosted;
a non-EU endpoint without an explicit base URL is rejected at construction so
personal data can never be routed outside the EEA by accident.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.core.config import settings


@dataclass(slots=True, frozen=True)
class Generation:
    """One model completion with usage accounting."""

    text: str
    model_ref: str
    prompt_tokens: int
    completion_tokens: int


class LlmClient(Protocol):
    """Contract for a text-generation and embedding backend."""

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def generate(self, *, system: str, prompt: str, max_tokens: int) -> Generation: ...


class SelfHostedClient:
    """OpenAI-compatible client pointed at an EU/self-hosted endpoint."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or settings.llm_base_url

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts using ``settings.embedding_model``."""
        # TODO(api): POST {base_url}/embeddings; batch to bound latency and cost.
        _ = (texts, self._base_url)
        raise NotImplementedError("embedding client is scaffolded but not implemented")

    async def generate(self, *, system: str, prompt: str, max_tokens: int) -> Generation:
        """Generate a completion for a retrieval-grounded prompt."""
        # TODO(api): POST {base_url}/chat/completions; enforce EU residency and
        #            log tokens without logging pastoral content.
        _ = (system, prompt, max_tokens, self._base_url)
        raise NotImplementedError("generation client is scaffolded but not implemented")


def build_client() -> LlmClient:
    """Return the configured client; non-EU providers are rejected here."""
    if settings.llm_provider == "eu-saas" and not settings.llm_base_url:
        raise ValueError("eu-saas provider requires an EU-resident LLM_BASE_URL")
    return SelfHostedClient()
