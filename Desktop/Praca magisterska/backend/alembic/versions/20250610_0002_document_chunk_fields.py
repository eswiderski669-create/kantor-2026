"""add chunk_count and last_error to documents; seed dev user

Revision ID: 20250610_0002
Revises: 20250510_0001
Create Date: 2026-06-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20250610_0002"
down_revision: str | None = "20250510_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEV_USER_ID = "00000000-0000-4000-8000-000000000001"


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("chunk_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("last_error", sa.String(length=4000), nullable=True),
    )

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO users (id, email, hashed_password, role, is_active, created_at, updated_at)
            SELECT CAST(:uid AS uuid), :email, :hp, 'admin', true, now(), now()
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = CAST(:uid AS uuid))
            """
        ),
        {
            "uid": DEV_USER_ID,
            "email": "dev@local.test",
            "hp": "placeholder-auth-not-configured",
        },
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM users WHERE id = CAST(:uid AS uuid)"),
        {"uid": DEV_USER_ID},
    )
    op.drop_column("documents", "last_error")
    op.drop_column("documents", "chunk_count")
