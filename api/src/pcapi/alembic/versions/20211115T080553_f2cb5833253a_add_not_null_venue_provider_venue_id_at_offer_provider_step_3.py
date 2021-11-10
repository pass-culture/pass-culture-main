"""add_not_null_venue_provider_venue_id_at_offer_provider_step_3
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f2cb5833253a"
down_revision = "010aba57cb3e"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("venue_provider", "venueIdAtOfferProvider", nullable=False)


def downgrade():
    pass
