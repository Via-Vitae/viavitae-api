"""Digital assessment funnel (DPIA-001)."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.assessment import AssessmentResult, AssessmentSubmit

router = APIRouter(tags=["assessment"])


@router.post(
    "/",
    response_model=AssessmentResult,
    status_code=status.HTTP_201_CREATED,
    summary="Record a completed funnel and return the recommended tier.",
)
async def submit_assessment(body: AssessmentSubmit) -> AssessmentResult:
    """Record a funnel submission, push a lead+deal to Bitrix24 (UTM kept).

    TODO(api): delegate to app.services.quotes_engine.recommend_tier and the
    bitrix24 mapper/sync, persist via the app.api.deps session seam, and return
    the AssessmentResult. Routers stay thin: validate, call a service, shape.
    """
    raise NotImplementedError("submit_assessment is scaffolded but not implemented")


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResult,
    summary="Fetch a stored assessment for the current tenant.",
)
async def get_assessment(assessment_id: str) -> AssessmentResult:
    """Fetch a stored assessment scoped to the resolved tenant (RLS)."""
    raise NotImplementedError("get_assessment is scaffolded but not implemented")
