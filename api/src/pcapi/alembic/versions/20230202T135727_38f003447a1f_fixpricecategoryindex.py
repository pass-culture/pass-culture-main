"""Add ix_stock_priceCategoryId index
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "38f003447a1f"
down_revision = "6b2fda23a359"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_stock_priceCategoryId"
        ON stock ("priceCategoryId")
        """
    )
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_stock_priceCategoryId"
        """
    )
