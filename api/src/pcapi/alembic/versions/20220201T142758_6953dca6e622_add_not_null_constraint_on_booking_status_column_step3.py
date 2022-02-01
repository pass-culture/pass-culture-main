"""add_not_null_constraint_on_booking_status_column_step3
"""
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "6953dca6e622"
down_revision = "e338d68fa7f1"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "booking",
        "status",
        existing_type=postgresql.ENUM("PENDING", "CONFIRMED", "USED", "CANCELLED", "REIMBURSED", name="booking_status"),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "booking",
        "status",
        existing_type=postgresql.ENUM("PENDING", "CONFIRMED", "USED", "CANCELLED", "REIMBURSED", name="booking_status"),
        nullable=True,
    )
