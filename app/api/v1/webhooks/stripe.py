"""Stripe webhook: signature verified, idempotent on event id (ADR-005).

Fail-closed by design: an event that cannot be verified is never acknowledged
with 2xx, because acknowledging tells Stripe to stop retrying and would silently
drop a real payment event. Unverified/unsigned events are rejected so the
provider keeps retrying until the handler is correctly implemented and keyed.
"""

from __future__ import annotations

from fastapi import APIRouter, Header, Request, Response, status

from app.core.config import settings
from app.core.errors import ApiError
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _secret_configured() -> bool:
    secret = settings.stripe_webhook_secret
    return bool(secret and secret.get_secret_value())


@router.post("", status_code=status.HTTP_200_OK)
async def receive_event(
    request: Request,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, str]:
    """Receive, verify and acknowledge a Stripe event.

    Verification contract (must be implemented before this endpoint is enabled):
    ``stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)``.
    """
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise ApiError("missing_signature", "Stripe-Signature header is required", status_code=400)
    if not _secret_configured():
        raise ApiError(
            "webhook_not_configured", "STRIPE_WEBHOOK_SECRET is not set", status_code=503
        )

    payload = await request.body()
    logger.info("stripe.event_received", bytes=len(payload), key=idempotency_key or "-")
    # TODO(api): 1) verify the signature above; reject with 400 on mismatch.
    #            2) upsert by provider event id; a replay returns the stored result.
    #            3) enqueue processing in app/workers; never block on it here.
    #            4) re-read amounts/status from the Stripe API; never trust the payload.
    raise ApiError(
        "not_implemented", "Stripe webhook processing is not implemented", status_code=501
    )


@router.get("/health")
async def webhook_health() -> Response:
    """Confirm the Stripe webhook secret is configured (no secret value returned)."""
    return Response(status_code=200 if _secret_configured() else 503)
