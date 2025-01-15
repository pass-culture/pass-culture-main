"""
Add NOT NULL constraint on "collective_stock.startDatetime" and "collective_stock.endDatetime"  (step 1 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a09ff41c9e94"
down_revision = "f512de569bde"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_stock" DROP CONSTRAINT IF EXISTS "collective_stock_startDatetime_not_null_constraint";
        ALTER TABLE "collective_stock" ADD CONSTRAINT "collective_stock_startDatetime_not_null_constraint" CHECK ("startDatetime" IS NOT NULL) NOT VALID;
        """
    )
    op.execute(
        """
        ALTER TABLE "collective_stock" DROP CONSTRAINT IF EXISTS "collective_stock_endDatetime_not_null_constraint";
        ALTER TABLE "collective_stock" ADD CONSTRAINT "collective_stock_endDatetime_not_null_constraint" CHECK ("endDatetime" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_stock_startDatetime_not_null_constraint", table_name="collective_stock")
    op.drop_constraint("collective_stock_endDatetime_not_null_constraint", table_name="collective_stock")
