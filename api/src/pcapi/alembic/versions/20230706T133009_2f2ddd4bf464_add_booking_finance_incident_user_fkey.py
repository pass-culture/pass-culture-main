"""
Add `booking_finance_incident.beneficiaryId` foreign key
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2f2ddd4bf464"
down_revision = "59ae101da397"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking_finance_incident", sa.Column("beneficiaryId", sa.BigInteger(), nullable=False))
    op.create_index(
        op.f("ix_booking_finance_incident_beneficiaryId"), "booking_finance_incident", ["beneficiaryId"], unique=False
    )
    op.create_foreign_key(
        "booking_finance_incident_beneficiaryId_fkey", "booking_finance_incident", "user", ["beneficiaryId"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("booking_finance_incident_beneficiaryId_fkey", "booking_finance_incident", type_="foreignkey")
    op.drop_index(op.f("ix_booking_finance_incident_beneficiaryId"), table_name="booking_finance_incident")
    op.drop_column("booking_finance_incident", "beneficiaryId")
