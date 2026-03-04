"""Add NOT NULL constraint on "pro_advice.venueId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9430b62a8545"
down_revision = "28587ae7713c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "pro_advice" DROP CONSTRAINT IF EXISTS "pro_advice_venueId_not_null_constraint";
        ALTER TABLE "pro_advice" ADD CONSTRAINT "pro_advice_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("pro_advice_venueId_not_null_constraint", table_name="pro_advice")
