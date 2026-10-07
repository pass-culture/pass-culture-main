"""Add NOT NULL constraint on "fraudulent_booking_tag.venueId" (step 2 of 4)"""

from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bc8d8220f0fa"
down_revision = "a7fae918196a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute(
            'ALTER TABLE "fraudulent_booking_tag" VALIDATE CONSTRAINT "fraudulent_booking_tag_venueId_not_null_constraint"'
        )
        op.execute(
            text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
            )
        )


def downgrade() -> None:
    pass
