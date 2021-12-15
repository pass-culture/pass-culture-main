"""
Add eligilibilityType to BeneficiaryFraudCheck
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "608d334310cd"
down_revision = "b5eab9709bdd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "beneficiary_fraud_check",
        sa.Column("eligibilityType", sa.TEXT(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("beneficiary_fraud_check", "eligibilityType")
