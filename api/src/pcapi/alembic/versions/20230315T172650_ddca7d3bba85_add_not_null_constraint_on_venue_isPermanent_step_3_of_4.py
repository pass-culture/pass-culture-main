"""Add NOT NULL constraint on "venue.isPermanent" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ddca7d3bba85"
down_revision = "05a6d0f9c246"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("venue", "isPermanent", nullable=False)


def downgrade():
    op.alter_column("venue", "isPermanent", nullable=True)
