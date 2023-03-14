"""Add NOT NULL constraint on "venue.dmsToken" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ed5d909b3525"
down_revision = "79f6edd135f5"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("venue_dmsToken_not_null_constraint", table_name="venue")


def downgrade():
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_dmsToken_not_null_constraint" CHECK ("dmsToken" IS NOT NULL) NOT VALID"""
    )
