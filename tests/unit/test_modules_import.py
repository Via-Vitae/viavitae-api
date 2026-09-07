"""Import smoke test: every model and schema module loads cleanly.

Catches typos, bad imports and Pydantic/SQLAlchemy misconfiguration at test time
rather than at first request. It also exercises the otherwise import-only stub
modules so a broken definition fails here.
"""

from __future__ import annotations

import importlib

import pytest

MODEL_MODULES = [
    "base",
    "assessment",
    "quote",
    "donation",
    "gis",
    "notification",
    "webhook_event",
    "ai_document",
    "ai_interaction",
]
SCHEMA_MODULES = ["common", "assessment", "quote", "donation", "ai", "gis", "webhook"]


@pytest.mark.parametrize("name", MODEL_MODULES)
def test_model_module_imports(name: str) -> None:
    importlib.import_module(f"app.models.{name}")


@pytest.mark.parametrize("name", SCHEMA_MODULES)
def test_schema_module_imports(name: str) -> None:
    importlib.import_module(f"app.schemas.{name}")
