"""
Add `booking_finance_incident.bookingId` foreign key
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d4d9ee033f5e"
down_revision = "e29dbc97ab38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking_finance_incident", sa.Column("bookingId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_booking_finance_incident_bookingId"),
        "booking_finance_incident",
        ["bookingId"],
        unique=False,
    )
    op.create_foreign_key(
        "booking_finance_incident_bookingId_fkey", "booking_finance_incident", "booking", ["bookingId"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("booking_finance_incident_bookingId_fkey", "booking_finance_incident", type_="foreignkey")
    op.drop_index(op.f("ix_booking_finance_incident_bookingId"), table_name="booking_finance_incident")
    op.drop_column("booking_finance_incident", "bookingId")
