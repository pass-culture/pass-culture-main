"""Fill in column: fraudulent_booking_tag.venueId"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2a8c112f9ca4"
down_revision = "38769750c0a2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""
        UPDATE fraudulent_booking_tag
        SET "venueId" = booking."venueId"
        FROM booking
        WHERE booking.id = fraudulent_booking_tag."bookingId"
        AND fraudulent_booking_tag."venueId" IS NULL;
    """)


def downgrade() -> None:
    pass
