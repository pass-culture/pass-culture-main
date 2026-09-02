"""Add ondelete=SET NULL on special_event_response_userId_fkey (2/3)"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e6ca71c9aa75"
down_revision = "d01b0452ca65"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "special_event_response_userId_fkey",
        "special_event_response",
        "user",
        ["userId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.drop_constraint("special_event_response_userId_fkey", "special_event_response", type_="foreignkey")
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
        )
    )
