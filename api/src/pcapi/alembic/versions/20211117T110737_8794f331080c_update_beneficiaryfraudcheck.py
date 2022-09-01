"""Update BeneficiaryFraudCheck
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "8794f331080c"
down_revision = "42ebfa8a45aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("beneficiary_fraud_check", sa.Column("reason", sa.Text(), nullable=True))
    op.add_column(
        "beneficiary_fraud_check",
        sa.Column(
            "reasonCodes",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "beneficiary_fraud_check",
        sa.Column("status", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("beneficiary_fraud_check", "status")
    op.drop_column("beneficiary_fraud_check", "reason_codes")
    op.drop_column("beneficiary_fraud_check", "reason")
