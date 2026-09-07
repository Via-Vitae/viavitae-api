#!/usr/bin/env bash
# Local development bootstrap: dependencies -> install -> migrate -> seed.
#
# Idempotent and safe to re-run. Fails loudly on the first error: there is no
# `|| true` anywhere, so a broken step never masquerades as success.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

log() { printf '==> %s\n' "$1"; }
die() { printf 'error: %s\n' "$1" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || die "docker is required but was not found on PATH"

# Prefer uv (the pinned toolchain); fall back to a plain venv + pip.
if command -v uv >/dev/null 2>&1; then
  log "Installing dependencies with uv (dev extra)"
  uv sync --extra dev
  RUN="uv run"
else
  log "uv not found; creating .venv and installing with pip"
  [ -d .venv ] || python3 -m venv .venv
  # shellcheck source=/dev/null
  source .venv/bin/activate
  pip install --upgrade pip >/dev/null
  pip install -e ".[dev]" >/dev/null
  RUN="python"
fi

log "Ensuring a local .env exists (never overwrite an existing one)"
[ -f .env ] || cp .env.example .env

log "Starting postgres (pgvector), redis and mailpit"
docker compose up -d --wait postgres redis mailpit

log "Applying migrations (no-op until the first revision lands)"
$RUN alembic upgrade head

log "Seeding the demo tenant (fictional data, dry-run by default)"
$RUN python scripts/seed_demo.py

log "Ready. Start the API with:"
log "  $RUN uvicorn app.main:app --reload --port 8000"
