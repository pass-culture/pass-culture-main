"""Add NOT NULL constraint on "venue.validationStatus" (step 2 of 4)"""

from alembic import op
from sqlalchemy import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "41383677de6f"
down_revision = "82a5ee3d4811"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "venue" VALIDATE CONSTRAINT "venue_validationStatus_not_null_constraint"')
    op.execute(
        text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
