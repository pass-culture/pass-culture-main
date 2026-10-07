"""Validate user_email_history_authorId_fkey constraint"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "de5e78443053"
down_revision = "7d4b6b018c02"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(sa.text("""ALTER TABLE user_email_history VALIDATE CONSTRAINT "user_email_history_authorId_fkey" """))
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
