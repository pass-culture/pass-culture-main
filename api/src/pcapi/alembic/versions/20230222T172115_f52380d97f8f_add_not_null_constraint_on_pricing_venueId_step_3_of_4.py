"""Add NOT NULL constraint on "pricing.venueId" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f52380d97f8f"
down_revision = "fef74efaaef4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("pricing", "venueId", nullable=False)


def downgrade():
    op.alter_column("pricing", "venueId", nullable=True)
