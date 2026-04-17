"""Validate constraint "cultural_outreach_offerId_fkey" """

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0d2b1fe1f0b9"
down_revision = "76687ea6ef2c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute('ALTER TABLE "cultural_outreach" VALIDATE CONSTRAINT "cultural_outreach_offerId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
