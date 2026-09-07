"""Webhook acknowledgement DTOs (ADR-005)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class WebhookAck(BaseModel):
    """The minimal acknowledgement returned once an event is verified and stored.

    ``replayed`` is true when the provider event id was already seen, so a
    duplicate delivery returns the stored outcome instead of re-running side
    effects.
    """

    model_config = ConfigDict(frozen=True)

    status: str
    provider_event_id: str | None = None
    replayed: bool = False
