"""Add NOT NULL constraint on "collective_stock.servicePrice" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6326d7f881b3"
down_revision = "d821984fa9f3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("collective_stock_servicePrice_not_null_constraint", table_name="collective_stock")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "collective_stock" ADD CONSTRAINT "collective_stock_servicePrice_not_null_constraint" CHECK ("servicePrice" IS NOT NULL) NOT VALID"""
    )
