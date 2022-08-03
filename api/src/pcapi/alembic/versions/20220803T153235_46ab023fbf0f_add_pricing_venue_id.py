"""Add pricing.venueId."""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "46ab023fbf0f"
down_revision = "4b549301f9f7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("pricing", sa.Column("venueId", sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column("pricing", "venueId")
