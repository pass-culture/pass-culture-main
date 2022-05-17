"""Add column isDuoOffers to venue_provider
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ebe9d1d80dcd"
down_revision = "f96e62709e85"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue_provider", sa.Column("isDuoOffers", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue_provider", "isDuoOffers")
