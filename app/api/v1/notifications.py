"""Email and SMS dispatch."""

from __future__ import annotations

from fastapi import APIRouter, status

router = APIRouter(tags=["notifications"])


@router.post("/", summary="Queue a notification for delivery.", status_code=status.HTTP_201_CREATED)
async def dispatch() -> dict[str, object]:
    """Queue a notification for delivery.

    TODO(api): wire the Pydantic request/response models from
    `docs/api/v1-openapi.json` and delegate to `app/services/`.
    """
    raise NotImplementedError("dispatch is scaffolded but not implemented")


@router.get("/{notification_id}", summary="Delivery status of a queued notification.")
async def get_status() -> dict[str, object]:
    """Delivery status of a queued notification.

    TODO(api): wire the Pydantic request/response models from
    `docs/api/v1-openapi.json` and delegate to `app/services/`.
    """
    raise NotImplementedError("get_status is scaffolded but not implemented")
