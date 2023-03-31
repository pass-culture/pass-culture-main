"""Add NOT NULL constraint on "pricing.pricingPointId" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3af4f7b52787"
down_revision = "ddb44c87b8cc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "pricing" DROP CONSTRAINT IF EXISTS "pricing_pricingPointId_not_null_constraint";
        ALTER TABLE "pricing" ADD CONSTRAINT "pricing_pricingPointId_not_null_constraint" CHECK ("pricingPointId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("pricing_pricingPointId_not_null_constraint", table_name="pricing")
