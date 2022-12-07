"""Add NOT NULL constraint on "venue.venueTypeCode" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bc9452222a80"
down_revision = "d66070f570d2"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("venue_venueTypeCode_not_null_constraint", table_name="venue")


def downgrade():
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_venueTypeCode_not_null_constraint" CHECK ("venueTypeCode" IS NOT NULL) NOT VALID"""
    )
