"""Add NOT NULL constraint on "pricing.venueId" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2054242de24a"
down_revision = "d2efd7e450c8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE "pricing" DROP CONSTRAINT IF EXISTS "pricing_venueId_not_null_constraint";
        ALTER TABLE "pricing" ADD CONSTRAINT "pricing_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("pricing_venueId_not_null_constraint", table_name="pricing")
