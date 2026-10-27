"""Bitrix24 event webhook: fail-closed STUB — processing is not implemented.

Bitrix24 outbound events are authenticated with the integration token/secret
embedded in the webhook URL. That verification and event-id idempotency (see
ADR-005) are the contract to implement, not current behavior: every request
that passes the input guards is refused with 501 ``not_implemented``.
Fail-closed: an event without a verifiable token is rejected rather than acted
upon, so a forged CRM event cannot mutate local state.
"""

from __future__ import annotations

from fastapi import APIRouter, Header, Request, Response, status

from app.core.config import settings
from app.core.errors import ApiError
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _secret_configured() -> bool:
    secret = settings.bitrix24_webhook_url
    return bool(secret and secret.get_secret_value())


@router.post("", status_code=status.HTTP_200_OK)
async def receive_event(
    request: Request,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, str]:
    """Refuse a Bitrix24 outbound CRM event without processing it (stub).

    Verification contract to implement before this endpoint may return 2xx:
    match the request token against the configured Bitrix24 webhook secret
    before parsing the body.
    """
    token = request.headers.get("x-bitrix-token") or request.query_params.get("token")
    if not token:
        raise ApiError("missing_signature", "Bitrix24 event token is required", status_code=400)
    if not _secret_configured():
        raise ApiError("webhook_not_configured", "BITRIX24_WEBHOOK_URL is not set", status_code=503)

    payload = await request.body()
    logger.info("bitrix24.event_received", bytes=len(payload), key=idempotency_key or "-")
    # TODO(api): 1) constant-time compare the token; reject 401 on mismatch.
    #            2) upsert by event id; a replay returns the stored result.
    #            3) enqueue CRM sync in app/workers; acknowledge quickly.
    raise ApiError(
        "not_implemented", "Bitrix24 event processing is not implemented", status_code=501
    )


@router.get("/health")
async def webhook_health() -> Response:
    """Confirm the Bitrix24 webhook is configured (no secret value returned)."""
    return Response(status_code=200 if _secret_configured() else 503)
