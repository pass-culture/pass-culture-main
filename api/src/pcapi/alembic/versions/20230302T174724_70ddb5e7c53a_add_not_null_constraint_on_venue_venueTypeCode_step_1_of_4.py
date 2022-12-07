"""Add NOT NULL constraint on "venue.venueTypeCode" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "70ddb5e7c53a"
down_revision = "a24e2d695e7c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_venueTypeCode_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_venueTypeCode_not_null_constraint" CHECK ("venueTypeCode" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("venue_venueTypeCode_not_null_constraint", table_name="venue")
