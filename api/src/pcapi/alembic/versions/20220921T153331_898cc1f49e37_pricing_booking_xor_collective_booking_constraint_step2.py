"""Validate constraint on pricing.bookingId XOR collectiveBookingId."""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "898cc1f49e37"
down_revision = "0eae46f5f7ea"
branch_labels = None
depends_on = None


table = "pricing"
constraint = "booking_xor_collective_booking_check"


def upgrade():
    op.execute(f"ALTER TABLE {table} VALIDATE CONSTRAINT {constraint}")


def downgrade():
    # Do nothing. The constraint will be removed only if the previous
    # migration is rollbacked.
    pass
