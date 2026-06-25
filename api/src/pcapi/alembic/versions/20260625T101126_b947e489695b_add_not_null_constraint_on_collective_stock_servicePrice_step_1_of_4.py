"""Add NOT NULL constraint on "collective_stock.servicePrice" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b947e489695b"
down_revision = "7771fd024d45"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_stock" DROP CONSTRAINT IF EXISTS "collective_stock_servicePrice_not_null_constraint";
        ALTER TABLE "collective_stock" ADD CONSTRAINT "collective_stock_servicePrice_not_null_constraint" CHECK ("servicePrice" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_stock_servicePrice_not_null_constraint", table_name="collective_stock")
