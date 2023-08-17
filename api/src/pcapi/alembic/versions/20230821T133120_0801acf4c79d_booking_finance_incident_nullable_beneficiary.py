"""Make booking incident beneficiary nullable (if concerns collective booking)
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0801acf4c79d"
down_revision = "f891eee42f86"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("booking_finance_incident", "beneficiaryId", existing_type=sa.BIGINT(), nullable=True)
    op.create_check_constraint(
        "booking_beneficiary_check",
        "booking_finance_incident",
        '"bookingId" IS NULL OR "beneficiaryId" IS NOT NULL',
    )


def downgrade() -> None:
    op.alter_column("booking_finance_incident", "beneficiaryId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_constraint("booking_beneficiary_check", "booking_finance_incident")
