"""Add index on booking.dateUsed"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "1e8ffcd7645a"
down_revision = "1f2f37dfc23d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_booking_dateUsed" ON booking ("dateUsed")
        """
    )
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    op.drop_index(op.f("ix_booking_dateUsed"), table_name="booking")
