"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Expand-contract rules:
  * additive first (new nullable column / new table), backfill, then constrain;
  * every migration must be reversible (`downgrade` is not a no-op);
  * tenant-scoped tables get their RLS policy in the same revision;
  * no data-destructive statement without a prior backup note in the docstring.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    """Apply the expand step."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Revert the expand step (contract happens in a later revision)."""
    ${downgrades if downgrades else "pass"}
