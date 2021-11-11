"""add_index_on_offer_subcategoryId

Revision ID: a9a2e51e8e24
Revises: f8f80e3ca099
Create Date: 2021-06-30 15:26:01.922044

"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "a9a2e51e8e24"
down_revision = "f8f80e3ca099"
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
