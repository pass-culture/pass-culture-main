"""Add NOT NULL constraint on "highlight.communication_date" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3407405ead9c"
down_revision = "5741397a3628"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "highlight" VALIDATE CONSTRAINT "highlight_communication_date_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
