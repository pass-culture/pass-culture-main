"""Add NOT NULL constraint on "venue.venueTypeCode" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d66070f570d2"
down_revision = "cee2ac7d4375"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("venue", "venueTypeCode", nullable=False)


def downgrade():
    op.alter_column("venue", "venueTypeCode", nullable=True)
