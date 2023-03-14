"""Add NOT NULL constraint on "venue.dmsToken" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "79f6edd135f5"
down_revision = "e18d97a2e849"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("venue", "dmsToken", nullable=False)


def downgrade():
    op.alter_column("venue", "dmsToken", nullable=True)
