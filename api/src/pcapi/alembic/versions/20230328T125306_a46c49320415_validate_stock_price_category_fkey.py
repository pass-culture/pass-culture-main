"""Validate price_category_offerId_fkey
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a46c49320415"
down_revision = "e61954337a7b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This upgrade failed in staging, it will fail certainly in production.
    # We will have to run it manually
    if settings.IS_PROD:
        return
    op.execute("COMMIT")
    # The timeout here has the same value (5 minutes) as `helm upgrade`.
    # If this migration fails, you'll have to execute it manually.
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "stock" VALIDATE CONSTRAINT "stock_priceCategoryId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
