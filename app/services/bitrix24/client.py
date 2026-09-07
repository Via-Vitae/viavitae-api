"""Bitrix24 REST client.

Thin, typed and deliberately boring: build the request, call, translate errors
into `Bitrix24Error`. Retries and failure isolation are the circuit breaker's
job (`circuit_breaker.py`), never the caller's.
"""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import SecretStr

from app.core.config import settings
from app.core.logging import get_logger
from app.services.bitrix24.circuit_breaker import CircuitBreaker

logger = get_logger(__name__)

LEAD_SOURCE_ID = "VIATAVAITAE_API"


class Bitrix24Error(RuntimeError):
    """Raised when Bitrix24 returns an error or is unreachable."""

    def __init__(self, code: str, message: str, status_code: int | None = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.status_code = status_code


def _resolve_base_url(webhook_url: str | SecretStr | None) -> str:
    """Normalise an explicit URL or the configured secret into a bare base URL."""
    configured = webhook_url if webhook_url is not None else settings.bitrix24_webhook_url
    if configured is None:
        raise Bitrix24Error("not_configured", "BITRIX24_WEBHOOK_URL is not set")
    secret = configured if isinstance(configured, SecretStr) else SecretStr(configured)
    return secret.get_secret_value().rstrip("/")


class Bitrix24Client:
    """REST adapter for leads, contacts and deals."""

    def __init__(
        self,
        webhook_url: str | SecretStr | None = None,
        breaker: CircuitBreaker | None = None,
    ) -> None:
        self._base = _resolve_base_url(webhook_url)
        self._breaker = breaker or CircuitBreaker(name="bitrix24")

    async def call(self, method: str, fields: dict[str, Any]) -> Any:
        """Invoke a Bitrix24 REST method with a timeout and circuit protection."""
        async with (
            self._breaker,
            httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client,
        ):
            response = await client.post(f"{self._base}/{method}", json=fields)

        if response.status_code >= 400:
            raise Bitrix24Error("http_error", response.text[:200], response.status_code)

        body = response.json()
        if body.get("error"):
            raise Bitrix24Error(str(body["error"]), str(body.get("error_description", "")))
        return body.get("result")

    async def add_lead(self, lead: dict[str, Any]) -> int:
        """Create a CRM lead from an assessment submission."""
        fields = {"fields": {**lead, "SOURCE_ID": LEAD_SOURCE_ID}}
        result = await self.call("crm.lead.add", fields)
        logger.info("bitrix24.lead_created", lead_id=result)
        return int(result)

    async def update_lead(self, lead_id: int, fields: dict[str, Any]) -> bool:
        """Update an existing lead."""
        return bool(await self.call("crm.lead.update", {"id": lead_id, "fields": fields}))
