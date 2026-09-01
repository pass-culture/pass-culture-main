"""Add ondelete=SET NULL on special_event_response_userId_fkey (3/3)"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2cfe1c7bcb34"
down_revision = "e6ca71c9aa75"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.execute("""ALTER TABLE special_event_response VALIDATE CONSTRAINT "special_event_response_userId_fkey" """)
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
        )
    )


def downgrade() -> None:
    pass
