"""Paysera callback: SS2 signature verified, idempotent on order id (ADR-005).

Paysera posts a callback whose integrity is protected by an ``ss2`` HMAC-style
digest computed over the ordered query parameters with the project sign
password. Fail-closed: without a verifiable signature the callback is rejected,
never acknowledged.
"""

from __future__ import annotations

from fastapi import APIRouter, Header, Request, Response, status

from app.core.config import settings
from app.core.errors import ApiError
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _secret_configured() -> bool:
    secret = settings.paysera_sign_password
    return bool(secret and secret.get_secret_value())


@router.post("", status_code=status.HTTP_200_OK)
async def receive_event(
    request: Request,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, str]:
    """Receive, verify and acknowledge a Paysera callback.

    Verification contract: recompute ``ss2`` over the sorted query parameters
    with ``settings.paysera_sign_password`` and compare in constant time.
    """
    signature = request.query_params.get("ss2") or request.headers.get("x-paysera-signature")
    if not signature:
        raise ApiError("missing_signature", "Paysera ss2 signature is required", status_code=400)
    if not _secret_configured():
        raise ApiError(
            "webhook_not_configured", "PAYSERA_SIGN_PASSWORD is not set", status_code=503
        )

    payload = await request.body()
    logger.info("paysera.event_received", bytes=len(payload), key=idempotency_key or "-")
    # TODO(api): 1) recompute and constant-time compare ss2; reject 400 on mismatch.
    #            2) upsert by order id; a replay returns the stored result.
    #            3) re-read the payment status from Paysera; never trust the callback amount.
    raise ApiError(
        "not_implemented", "Paysera callback processing is not implemented", status_code=501
    )


@router.get("/health")
async def webhook_health() -> Response:
    """Confirm the Paysera sign password is configured (no secret value returned)."""
    return Response(status_code=200 if _secret_configured() else 503)
