"""make_ix_collective_stock_collectiveOfferId_unique
"""
from alembic import op

from pcapi import settings


revision = "6ee927d299b1"
down_revision = "0efdf36fd5d7"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.drop_index("ix_collective_stock_collectiveOfferId", table_name="collective_stock")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_collective_stock_collectiveOfferId" ON collective_stock ("collectiveOfferId")
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
            """
    )


def downgrade():
    op.drop_index("ix_collective_stock_collectiveOfferId", table_name="collective_stock")
    op.create_index("ix_collective_stock_collectiveOfferId", "collective_stock", ["collectiveOfferId"], unique=False)
