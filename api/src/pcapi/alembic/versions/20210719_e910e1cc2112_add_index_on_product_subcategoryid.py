"""add_index_on_product_subcategoryId

Revision ID: e910e1cc2112
Revises: d1c3b30ef70d
Create Date: 2021-07-19 14:29:22.866117

"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "e910e1cc2112"
down_revision = "d1c3b30ef70d"
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
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_product_subcategoryId" ON product ("subcategoryId")
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
        DROP INDEX CONCURRENTLY IF EXISTS "ix_product_subcategoryId"
        """
    )
