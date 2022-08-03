"""Add index and foreign key constraint on pricing.venueId
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "934d0e50595f"
down_revision = "4054f720ac9f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_pricing_venueId" ON pricing ("venueId")')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")

    # The ALTER TABLE query would lock prod and staging for too long.
    # We probably need to disable the "price_bookings" prod and add
    # the index/foreign key during the off-hours.
    if not (settings.IS_PROD or settings.IS_STAGING):
        op.create_foreign_key("pricing_venueId_fkey", "pricing", "venue", ["venueId"], ["id"])


def downgrade():
    op.execute('ALTER TABLE pricing DROP CONSTRAINT IF EXISTS "pricing_venueId_fkey"')
    op.execute('DROP INDEX IF EXISTS "ix_pricing_venueId"')
