"""add_eligibility_type_to_beneficiary_fraud_review
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "83f944319ccf"
down_revision = "dcfd7657a244"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("beneficiary_fraud_review", sa.Column("eligibilityType", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("beneficiary_fraud_review", "eligibilityType")
