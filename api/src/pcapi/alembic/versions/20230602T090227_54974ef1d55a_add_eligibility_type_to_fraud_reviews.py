"""Add eligibility column to BeneficiaryFraudReview table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "54974ef1d55a"
down_revision = "cf9c67b851f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("beneficiary_fraud_review", sa.Column("eligibilityType", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("beneficiary_fraud_review", "eligibilityType")
