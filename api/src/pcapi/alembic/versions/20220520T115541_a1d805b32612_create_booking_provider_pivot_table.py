"""create_booking_provider_pivot_table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1d805b32612"
down_revision = "4400cd98902e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "booking_provider_pivot",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.Column("bookingProviderId", sa.BigInteger(), nullable=False),
        sa.Column("idAtProvider", sa.Text(), nullable=False),
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
        sa.UniqueConstraint("venueId"),
        sa.UniqueConstraint("venueId", "bookingProviderId", name="unique_pivot_venue_booking_provider"),
    )


def downgrade() -> None:
    op.drop_table("booking_provider_pivot")
