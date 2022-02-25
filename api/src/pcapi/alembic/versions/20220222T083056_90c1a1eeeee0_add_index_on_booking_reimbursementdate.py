"""add_index_on_booking_reimbursementDate
"""
from alembic import op

# revision identifiers, used by Alembic.
from pcapi import settings


revision = "90c1a1eeeee0"
down_revision = "56c6d018551c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_booking_reimbursementDate" ON booking ("reimbursementDate")
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
            """
    )


def downgrade():
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_booking_reimbursementDate"
        """
    )
