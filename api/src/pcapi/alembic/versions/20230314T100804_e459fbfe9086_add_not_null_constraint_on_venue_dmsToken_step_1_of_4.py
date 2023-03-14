"""Add NOT NULL constraint on "venue.dmsToken" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e459fbfe9086"
down_revision = "bc9452222a80"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_dmsToken_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_dmsToken_not_null_constraint" CHECK ("dmsToken" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("venue_dmsToken_not_null_constraint", table_name="venue")
