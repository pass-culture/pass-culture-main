"""update_unicity_constraint_for_venue_booking_provider
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ce0fcf03be9a"
down_revision = "08899a47bb54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("unique_venue_booking_provider", "venue_booking_provider", type_="unique")
    op.create_unique_constraint(
        "unique_venue_booking_provider", "venue_booking_provider", ["venueId", "bookingProviderId"]
    )


def downgrade() -> None:
    op.drop_constraint("unique_venue_booking_provider", "venue_booking_provider", type_="unique")
    op.create_unique_constraint(
        "unique_venue_booking_provider", "venue_booking_provider", ["venueId", "bookingProviderId", "idAtProvider"]
    )
