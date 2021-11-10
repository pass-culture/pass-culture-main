"""add_not_null_venue_provider_venue_id_at_offer_provider_step_4
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "32c7ca9be253"
down_revision = "f2cb5833253a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("venueid_at_offer_provider_not_null_constraint", table_name="venue_provider")


def downgrade():
    op.execute(
        """
            ALTER TABLE venue_provider ADD CONSTRAINT venueid_at_offer_provider_not_null_constraint CHECK ("venueIdAtOfferProvider" IS NOT NULL) NOT VALID;
        """
    )
