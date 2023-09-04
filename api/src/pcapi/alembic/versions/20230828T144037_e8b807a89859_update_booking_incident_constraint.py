"""Update booking finance incident constraint to have either a individual or a collective booking
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e8b807a89859"
down_revision = "41c2cf970790"
branch_labels = None
depends_on = None

table_name = "booking_finance_incident"


def upgrade() -> None:
    op.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS "booking_beneficiary_check"')
    op.create_check_constraint(
        "booking_finance_incident_check",
        table_name,
        '("bookingId" IS NOT NULL AND "beneficiaryId" IS NOT NULL AND "collectiveBookingId" IS NULL) '
        'OR ("collectiveBookingId" IS NOT NULL AND "bookingId" IS NULL AND "beneficiaryId" IS NULL)',
    )


def downgrade() -> None:
    op.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS "booking_beneficiary_check"')
    op.create_check_constraint(
        "booking_beneficiary_check",
        table_name,
        '"bookingId" IS NULL OR "beneficiaryId" IS NOT NULL',
    )
