"""Aggregate router for `/v1`.

Mount order matters for OpenAPI grouping. Routers stay thin: validate input,
call a service, shape the response. No business logic here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    ai_pastoral,
    assessment,
    crm_dashboard,
    donations,
    gis,
    health,
    notifications,
    quotes,
)
from app.api.v1.webhooks.router import webhook_router

api_router = APIRouter(tags=["v1"])
api_router.include_router(health.router)
api_router.include_router(assessment.router, prefix="/assessment")
api_router.include_router(quotes.router, prefix="/quotes")
api_router.include_router(donations.router, prefix="/donations")
api_router.include_router(ai_pastoral.router, prefix="/ai")
api_router.include_router(gis.router, prefix="/gis")
api_router.include_router(notifications.router, prefix="/notifications")
api_router.include_router(crm_dashboard.router, prefix="/crm")
api_router.include_router(webhook_router, prefix="/webhooks")
