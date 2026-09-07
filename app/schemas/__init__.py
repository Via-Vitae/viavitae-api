"""Pydantic v2 request/response DTOs -- the API's data contract.

Routers import the specific submodule they need (``app.schemas.assessment``);
these models are the single source of truth for request/response shapes and are
what ``docs/api/v1-openapi.json`` is generated from. Money is always integer
minor units plus a currency code; personal data is minimised per the DPIAs.
"""
