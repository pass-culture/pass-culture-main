"""
Add `booking_finance_incident.finance_incidentId` foreign key
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c1aaa9540b1b"
down_revision = "d4d9ee033f5e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking_finance_incident", sa.Column("incidentId", sa.BigInteger(), nullable=False))
    op.create_index(
        op.f("ix_booking_finance_incident_incidentId"),
        "booking_finance_incident",
        ["incidentId"],
        unique=False,
    )
    op.create_foreign_key(
        "booking_finance_incident_incidentId_fkey",
        "booking_finance_incident",
        "finance_incident",
        ["incidentId"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("booking_finance_incident_incidentId_fkey", "booking_finance_incident", type_="foreignkey")
    op.drop_index(op.f("ix_booking_finance_incident_incidentId"), table_name="booking_finance_incident")
    op.drop_column("booking_finance_incident", "incidentId")
