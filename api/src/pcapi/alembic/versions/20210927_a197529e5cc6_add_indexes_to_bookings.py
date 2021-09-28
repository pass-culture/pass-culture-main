"""add_indexes_to_bookings
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a197529e5cc6"
down_revision = "3b2ea23b8cf0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_booking_is_used"
        ON
            booking ("isUsed")
        WHERE
            "isUsed" is false
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
        DROP INDEX CONCURRENTLY IF EXISTS "ix_booking_is_used"
        """
    )
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_booking_date_created"
        """
    )
