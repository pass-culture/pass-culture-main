"""add_booking_provider_and_venue_booking_provider_tables
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d6d472d2dfad"
down_revision = "c00ea85d88c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "booking_provider",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Enum("CINE_DIGITAL_SERVICE", name="bookingprovidername"), nullable=False),
        sa.Column("apiUrl", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "venue_booking_provider",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("isActive", sa.Boolean(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("bookingProviderId", sa.BigInteger(), nullable=False),
        sa.Column("idAtProvider", sa.String(length=70), nullable=False),
        sa.Column("token", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bookingProviderId"],
            ["booking_provider.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_venue_booking_provider_venueId"), "venue_booking_provider", ["venueId"], unique=False)
    op.create_unique_constraint(
        "unique_venue_booking_provider", "venue_booking_provider", ["venueId", "bookingProviderId", "idAtProvider"]
    )


def downgrade() -> None:
    op.drop_constraint("unique_venue_booking_provider", "venue_booking_provider", type_="unique")
    op.drop_index(op.f("ix_venue_booking_provider_venueId"), table_name="venue_booking_provider")
    op.drop_table("venue_booking_provider")
    op.drop_table("booking_provider")
    op.execute("DROP TYPE bookingprovidername")
