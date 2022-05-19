"""modify_venue_booking_provider_table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ffb709b42fae"
down_revision = "52b7d4d03980"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue_booking_provider", sa.Column("isDuo", sa.Boolean(), nullable=False))
    op.add_column("venue_booking_provider", sa.Column("venueProviderId", sa.BigInteger(), nullable=False))
    op.drop_constraint("unique_venue_booking_provider", "venue_booking_provider", type_="unique")
    op.create_unique_constraint(
        "unique_venue_booking_provider", "venue_booking_provider", ["venueProviderId", "bookingProviderId"]
    )
    op.drop_index("ix_venue_booking_provider_venueId", table_name="venue_booking_provider")
    op.drop_constraint("venue_booking_provider_venueId_fkey", "venue_booking_provider", type_="foreignkey")
    op.create_foreign_key(None, "venue_booking_provider", "venue_provider", ["venueProviderId"], ["id"])
    op.drop_column("venue_booking_provider", "isActive")
    op.drop_column("venue_booking_provider", "id")
    op.drop_column("venue_booking_provider", "venueId")
    op.drop_column("venue_booking_provider", "idAtProvider")


def downgrade() -> None:
    op.add_column(
        "venue_booking_provider", sa.Column("idAtProvider", sa.VARCHAR(length=70), autoincrement=False, nullable=False)
    )
    op.add_column("venue_booking_provider", sa.Column("venueId", sa.BIGINT(), autoincrement=False, nullable=False))
    op.add_column("venue_booking_provider", sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False))
    op.add_column("venue_booking_provider", sa.Column("isActive", sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_constraint(None, "venue_booking_provider", type_="foreignkey")
    op.create_foreign_key("venue_booking_provider_venueId_fkey", "venue_booking_provider", "venue", ["venueId"], ["id"])
    op.create_index("ix_venue_booking_provider_venueId", "venue_booking_provider", ["venueId"], unique=False)
    op.drop_constraint("unique_venue_booking_provider", "venue_booking_provider", type_="unique")
    op.create_unique_constraint(
        "unique_venue_booking_provider", "venue_booking_provider", ["venueId", "bookingProviderId"]
    )
    op.drop_column("venue_booking_provider", "venueProviderId")
    op.drop_column("venue_booking_provider", "isDuo")
