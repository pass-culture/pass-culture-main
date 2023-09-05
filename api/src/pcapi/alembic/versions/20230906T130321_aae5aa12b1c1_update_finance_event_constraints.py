"""Update finance event constraints
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "aae5aa12b1c1"
down_revision = "2edee580308f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("finance_event", sa.Column("bookingFinanceIncidentId", sa.BigInteger(), nullable=True))
    op.create_index(
        "idx_uniq_booking_finance_incident_id",
        "finance_event",
        ["bookingFinanceIncidentId", "motive"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'ready')"),
    )
    op.create_index(
        op.f("ix_finance_event_bookingFinanceIncidentId"), "finance_event", ["bookingFinanceIncidentId"], unique=False
    )
    op.create_foreign_key(None, "finance_event", "booking_finance_incident", ["bookingFinanceIncidentId"], ["id"])
    op.drop_constraint("finance_event_check", "finance_event")
    op.create_check_constraint(
        "finance_event_check",
        "finance_event",
        'num_nonnulls("bookingId", "collectiveBookingId", "bookingFinanceIncidentId") = 1',
    )


def downgrade() -> None:
    op.drop_constraint("finance_event_check", "finance_event")
    op.drop_index(op.f("ix_finance_event_bookingFinanceIncidentId"), table_name="finance_event")
    op.drop_index(
        "idx_uniq_booking_finance_incident_id",
        table_name="finance_event",
        postgresql_where=sa.text("status IN ('pending', 'ready')"),
    )
    op.drop_column("finance_event", "bookingFinanceIncidentId")
    op.create_check_constraint(
        "finance_event_check", "finance_event", 'num_nonnulls("bookingId", "collectiveBookingId") = 1'
    )
