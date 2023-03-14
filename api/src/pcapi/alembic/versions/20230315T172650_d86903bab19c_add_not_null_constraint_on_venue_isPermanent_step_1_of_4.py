"""Add NOT NULL constraint on "venue.isPermanent" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d86903bab19c"
down_revision = "e13e5a7d2e23"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_isPermanent_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_isPermanent_not_null_constraint" CHECK ("isPermanent" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("venue_isPermanent_not_null_constraint", table_name="venue")
