"""Update constraint: no partial incident on collective bookings
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "65a8910cf1db"
down_revision = "10b54017d02a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Table is still empty in production
    op.drop_constraint("booking_finance_incident_check", "booking_finance_incident")
    op.create_check_constraint(
        "booking_finance_incident_check",
        "booking_finance_incident",
        '("bookingId" IS NOT NULL AND "beneficiaryId" IS NOT NULL AND "collectiveBookingId" IS NULL) '
        'OR ("collectiveBookingId" IS NOT NULL AND "bookingId" IS NULL AND "beneficiaryId" IS NULL AND "newTotalAmount" = 0)',
    )


def downgrade() -> None:
    op.drop_constraint("booking_finance_incident_check", "booking_finance_incident")
    op.create_check_constraint(
        "booking_finance_incident_check",
        "booking_finance_incident",
        '("bookingId" IS NOT NULL AND "beneficiaryId" IS NOT NULL AND "collectiveBookingId" IS NULL) '
        'OR ("collectiveBookingId" IS NOT NULL AND "bookingId" IS NULL AND "beneficiaryId" IS NULL)',
    )
