"""Add NOT VALID constraint on pricing.bookingId XOR collectiveBookingId."""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0eae46f5f7ea"
down_revision = "8b325869c549"
branch_labels = None
depends_on = None


table = "pricing"
constraint = "booking_xor_collective_booking_check"


def upgrade():
    op.execute(
        f"""
        ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{constraint}";
        ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" CHECK (NUM_NONNULLS("bookingId", "collectiveBookingId") = 1) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint(constraint, table)
