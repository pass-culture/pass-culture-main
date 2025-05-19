"""Add NOT NULL constraint on "special_event.endImportDate" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cb4aae091f35"
down_revision = "4a9101c5aa05"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # less than 100 lines to update
    op.execute('UPDATE special_event SET "endImportDate" = "eventDate" + 7 WHERE "endImportDate" IS NULL')
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "special_event" VALIDATE CONSTRAINT "special_event_endImportDate_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
