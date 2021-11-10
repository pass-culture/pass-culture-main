"""add_not_null_venue_provider_venue_id_at_offer_provider_step_2
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a0a822d365ac"
down_revision = "5ff1b52e2f08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            ALTER TABLE venue_provider DROP CONSTRAINT IF EXISTS venueid_at_offer_provider_not_null_constraint;
            ALTER TABLE venue_provider ADD CONSTRAINT venueid_at_offer_provider_not_null_constraint CHECK ("venueIdAtOfferProvider" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venueid_at_offer_provider_not_null_constraint", table_name="venue_provider")
