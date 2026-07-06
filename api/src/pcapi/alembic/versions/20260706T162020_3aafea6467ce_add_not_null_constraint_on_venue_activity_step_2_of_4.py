"""Add NOT NULL constraint on "venue.activity" (step 2 of 4)"""

from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3aafea6467ce"
down_revision = "792091afeb3d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "venue" VALIDATE CONSTRAINT "venue_activity_not_null_constraint"')
        op.execute(
            text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
            )
        )


def downgrade() -> None:
    pass
