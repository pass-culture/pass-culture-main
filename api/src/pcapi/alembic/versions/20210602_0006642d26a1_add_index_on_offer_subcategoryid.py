"""add index on subcategoryId

Revision ID: 0006642d26a1
Revises: 380c28602547
Create Date: 2021-06-02 15:15:45.331394

"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "0006642d26a1"
down_revision = "380c28602547"
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
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_subcategoryId" ON offer ("subcategoryId")
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
        DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_subcategoryId"
        """
    )
