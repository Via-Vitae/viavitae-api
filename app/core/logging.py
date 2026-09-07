"""Structured JSON logging and request correlation.

Rule: never log personal data, tokens, card numbers or pastoral content. Log
identifiers and outcomes instead. `request_id` is generated per request and
propagated to outbound calls so a trace can be rebuilt across web -> api ->
provider.
"""

from __future__ import annotations

import logging
import sys
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

import structlog
from fastapi import Request, Response
from structlog.typing import EventDict, Processor, WrappedLogger

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
tenant_id_ctx: ContextVar[str] = ContextVar("tenant_id", default="-")

REDACTED_KEYS = frozenset(
    {
        "password",
        "token",
        "secret",
        "authorization",
        "cookie",
        "card_number",
        "iban",
        "api_key",
        "webhook_secret",
        "signature",
    }
)


def _add_correlation(_logger: WrappedLogger, _method: str, event_dict: EventDict) -> EventDict:
    """Attach request/tenant correlation ids to every log record."""
    event_dict["request_id"] = request_id_ctx.get()
    event_dict["tenant_id"] = tenant_id_ctx.get()
    return event_dict


def _redact(_logger: WrappedLogger, _method: str, event_dict: EventDict) -> EventDict:
    """Replace values of sensitive keys before rendering."""
    for key in list(event_dict):
        if key.lower() in REDACTED_KEYS:
            event_dict[key] = "[redacted]"
    return event_dict


def configure_logging(level: str = "INFO", json_output: bool = True) -> None:
    """Configure structlog and the stdlib bridge. Call once at startup."""
    logging.basicConfig(stream=sys.stdout, level=level.upper(), format="%(message)s")

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_correlation,
        _redact,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    processors.append(
        structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level.upper())),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a bound logger for a module."""
    bound: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return bound


async def request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Correlate logs and responses with a request id."""
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_ctx.reset(token)
    response.headers["x-request-id"] = request_id
    return response
