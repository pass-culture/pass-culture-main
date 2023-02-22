"""Add NOT NULL constraint on "pricing.venueId" (step 2 of 4)"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fef74efaaef4"
down_revision = "2054242de24a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "pricing" VALIDATE CONSTRAINT "pricing_venueId_not_null_constraint"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade():
    pass
