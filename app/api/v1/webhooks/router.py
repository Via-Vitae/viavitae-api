"""Webhook router.

Every webhook endpoint must:
1. verify the provider signature before parsing the body;
2. be idempotent on the provider event id (ADR-005);
3. acknowledge quickly and process asynchronously;
4. never trust amounts or identifiers from the payload — re-read them from the
   provider API.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.webhooks import bitrix24, paysera, stripe

webhook_router = APIRouter(tags=["webhooks"])
webhook_router.include_router(stripe.router, prefix="/stripe")
webhook_router.include_router(paysera.router, prefix="/paysera")
webhook_router.include_router(bitrix24.router, prefix="/bitrix24")
