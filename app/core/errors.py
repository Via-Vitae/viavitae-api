"""Unified error envelope and exception handlers (ADR-006).

Every error leaves the service in one stable shape so clients branch on a
machine-readable ``code`` rather than parsing prose::

    {"error": {"code": str, "message": str, "details": object, "request_id": str}}

Internals and stack traces are never returned to clients; they are logged with
the request id so a support ticket can be correlated to a trace. Scaffolded
endpoints raise ``NotImplementedError`` and answer ``501`` (never a ``500``
stack trace) so the not-implemented contract is explicit and testable.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_ctx

logger = get_logger(__name__)


class ApiError(Exception):
    """A domain error that maps to a stable HTTP status and envelope code."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details: dict[str, Any] = details or {}


def envelope(code: str, message: str, details: Any = None) -> dict[str, Any]:
    """Build the single error shape used by every handler."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": request_id_ctx.get(),
        }
    }


async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    """Render a domain error as the envelope."""
    logger.warning("api.error", code=exc.code, status=exc.status_code, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code, content=envelope(exc.code, exc.message, exc.details)
    )


async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Render framework HTTP errors (404, 405, ...) as the envelope."""
    detail = str(exc.detail)
    code = detail.lower().replace(" ", "_") if detail else f"http_{exc.status_code}"
    logger.info("api.http_error", status=exc.status_code, path=request.url.path)
    return JSONResponse(status_code=exc.status_code, content=envelope(code, detail))


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Render Pydantic validation failures without echoing submitted values."""
    details = [
        {"loc": list(err.get("loc", ())), "msg": err.get("msg"), "type": err.get("type")}
        for err in exc.errors()
    ]
    logger.info("api.validation_error", path=request.url.path, count=len(details))
    return JSONResponse(
        status_code=422,  # Unprocessable Content
        content=envelope("validation_error", "Request validation failed.", details),
    )


async def handle_not_implemented(request: Request, exc: NotImplementedError) -> JSONResponse:
    """Scaffolded endpoints answer 501, never a 500 stack trace."""
    logger.error("api.not_implemented", path=request.url.path, detail=str(exc))
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content=envelope("not_implemented", str(exc) or "Endpoint not implemented."),
    )


async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    """Last resort: log the detail, return an opaque 500."""
    logger.exception("api.unhandled_error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=envelope("internal_error", "An unexpected error occurred."),
    )


# A single dispatch table binds each exception class to its handler; registering
# from the table keeps the mapping and the registration impossible to drift apart.
_HANDLERS: list[tuple[type[Exception], Callable[..., Any]]] = [
    (ApiError, handle_api_error),
    (StarletteHTTPException, handle_http_exception),
    (RequestValidationError, handle_validation_error),
    (NotImplementedError, handle_not_implemented),
    (Exception, handle_unexpected),
]


def register_error_handlers(app: FastAPI) -> None:
    """Attach every handler to the app (called from the app factory)."""
    for exc_class, handler in _HANDLERS:
        app.add_exception_handler(exc_class, handler)
