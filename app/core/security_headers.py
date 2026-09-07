"""Security headers and hardened defaults for every response."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

HEADERS: dict[str, str] = {
    "strict-transport-security": "max-age=63072000; includeSubDomains; preload",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-site",
    "cache-control": "no-store",
    "content-security-policy": (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    ),
}

# Headers that identify the server/runtime and must never reach a client.
_STRIPPED_RESPONSE_HEADERS = ("server", "x-powered-by")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach security headers and strip server identification."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for header, value in HEADERS.items():
            response.headers.setdefault(header, value)
        # Starlette's MutableHeaders has no .pop(); delete explicitly and guard
        # membership so a missing header is not an error.
        for header in _STRIPPED_RESPONSE_HEADERS:
            if header in response.headers:
                del response.headers[header]
        return response
