"""
Add NOT NULL constraint on "collective_stock.startDatetime" and "collective_stock.endDatetime" (step 4 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a8d2c442cc67"
down_revision = "4302137d444a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("collective_stock_startDatetime_not_null_constraint", table_name="collective_stock")
    op.drop_constraint("collective_stock_endDatetime_not_null_constraint", table_name="collective_stock")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "collective_stock" ADD CONSTRAINT "collective_stock_startDatetime_not_null_constraint" CHECK ("startDatetime" IS NOT NULL) NOT VALID"""
    )
    op.execute(
        """ALTER TABLE "collective_stock" ADD CONSTRAINT "collective_stock_endDatetime_not_null_constraint" CHECK ("endDatetime" IS NOT NULL) NOT VALID"""
    )
