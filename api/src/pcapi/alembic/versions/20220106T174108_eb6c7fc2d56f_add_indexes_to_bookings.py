"""add indexes to bookings
"""
from alembic import op


revision = "eb6c7fc2d56f"
down_revision = "6bb141d40d77"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_booking_status"
        ON
            booking ("status")
        """
    )
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_booking_date_created"
        ON
            booking ("dateCreated")
        """
    )


def downgrade():
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_booking_status"
        """
    )
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_booking_date_created"
        """
    )
