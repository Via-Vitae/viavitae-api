# syntax=docker/dockerfile:1

# Multi-stage build. Dependencies are resolved from the committed uv.lock with
# --frozen, so an image built today is byte-for-byte reproducible from the same
# lock (no floating version ranges at build time). uv itself is pinned by tag and
# copied from the official image -- no curl|sh installer.

FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /usr/local/bin/
# libpq-dev/build-essential are only needed if a dependency ships no wheel; they
# stay in the builder stage and never reach the runtime image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Install dependencies first (cached across source changes), then the project.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home /app app
WORKDIR /app
# The virtualenv (dependencies + installed project) from the builder.
COPY --from=builder --chown=app:app /app/.venv /app/.venv
# Source is copied too: alembic.ini resolves migrations relative to WORKDIR
# (script_location = app/db/migrations), so the tree must exist at runtime.
# There is deliberately no `COPY alembic ./alembic` -- that directory does not
# exist; migrations live under app/db/migrations and arrive with app/.
COPY --chown=app:app app ./app
COPY --chown=app:app alembic.ini ./
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD curl --fail --silent http://127.0.0.1:8000/health/live || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
