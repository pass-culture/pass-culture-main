"""
Add `booking_finance_incident.collective_bookingId` foreign key
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "59ae101da397"
down_revision = "c1aaa9540b1b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking_finance_incident", sa.Column("collectiveBookingId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_booking_finance_incident_collectiveBookingId"),
        "booking_finance_incident",
        ["collectiveBookingId"],
        unique=False,
    )
    op.create_foreign_key(
        "booking_finance_incident_collectiveBookingId_fkey",
        "booking_finance_incident",
        "collective_booking",
        ["collectiveBookingId"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "booking_finance_incident_collectiveBookingId_fkey", "booking_finance_incident", type_="foreignkey"
    )
    op.drop_index(op.f("ix_booking_finance_incident_collectiveBookingId"), table_name="booking_finance_incident")
    op.drop_column("booking_finance_incident", "collectiveBookingId")
