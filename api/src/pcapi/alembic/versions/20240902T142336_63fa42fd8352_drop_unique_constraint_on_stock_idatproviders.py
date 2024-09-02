"""
Drop unique constraint on stock.idAtProviders
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "63fa42fd8352"
down_revision = "d8a0801f62e2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "stock" DROP CONSTRAINT IF EXISTS "stock_idAtProviders_key";
        """
    )


def downgrade() -> None:
    # `COMMIT` and isolation of the `CREATE UNIQUE INDEX CONCURRENTLY` command necessary since it cannot run in a transaction block
    op.execute("COMMIT;")
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "stock_idAtProviders_key" ON stock ("idAtProviders");
        """
    )
    op.execute("BEGIN;")
