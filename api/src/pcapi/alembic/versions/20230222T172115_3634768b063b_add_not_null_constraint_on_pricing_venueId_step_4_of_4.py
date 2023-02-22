"""Add NOT NULL constraint on "pricing.venueId" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3634768b063b"
down_revision = "f52380d97f8f"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("pricing_venueId_not_null_constraint", table_name="pricing")


def downgrade():
    op.execute(
        """ALTER TABLE "pricing" ADD CONSTRAINT "pricing_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID"""
    )
