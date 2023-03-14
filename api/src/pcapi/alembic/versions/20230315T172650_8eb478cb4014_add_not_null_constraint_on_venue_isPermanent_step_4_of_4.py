"""Add NOT NULL constraint on "venue.isPermanent" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8eb478cb4014"
down_revision = "ddca7d3bba85"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("venue_isPermanent_not_null_constraint", table_name="venue")


def downgrade():
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_isPermanent_not_null_constraint" CHECK ("isPermanent" IS NOT NULL) NOT VALID"""
    )
