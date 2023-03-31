"""Add NOT NULL constraint on "pricing.pricingPointId" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "da9509688eb1"
down_revision = "c3df7b8e8745"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("pricing_pricingPointId_not_null_constraint", table_name="pricing")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "pricing" ADD CONSTRAINT "pricing_pricingPointId_not_null_constraint" CHECK ("pricingPointId" IS NOT NULL) NOT VALID"""
    )
