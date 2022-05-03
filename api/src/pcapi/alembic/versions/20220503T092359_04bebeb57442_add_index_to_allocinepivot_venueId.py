"""add index to allocine_pivot venueId
"""
from alembic import op

# revision identifiers, used by Alembic.
from pcapi import settings


revision = "04bebeb57442"
down_revision = "6ff9746fd28a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_allocine_pivot_venueId" ON allocine_pivot ("venueId")
        """
    )
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    pass
