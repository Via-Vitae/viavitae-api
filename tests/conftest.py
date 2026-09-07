"""Shared pytest fixtures.

Rules: tests never touch production endpoints, never use real personal data and
never require network access (providers are faked in ``tests/contract/``). A dummy
``DATABASE_URL`` is set before the app is imported so the suite runs offline; the
ASGI transport does not trigger the lifespan, so no real connection is opened for
unit/api tests. Tests that need a live, multi-schema database are marked
``isolation`` and skip offline (they run in the DB-enabled CI job).
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# Required settings must exist before app.core.config is imported (it validates
# at import time and fails fast), so this line sits immediately above the import.
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/viavitae_test")

from app.main import create_app


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Application under test."""
    return create_app()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP client bound to the app without opening a socket."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://testserver") as async_client:
        yield async_client


@pytest.fixture
def tenant_id() -> str:
    """A deterministic fake tenant id for isolation tests."""
    return "11111111-1111-4111-8111-111111111111"


@pytest.fixture
def tenant_headers() -> dict[str, str]:
    """Headers that resolve a tenant without a live auth provider."""
    return {"X-Tenant": "anne"}
