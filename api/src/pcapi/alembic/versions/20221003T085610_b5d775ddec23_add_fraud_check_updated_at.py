"""Add beneficiary_fraud_check updatedAt column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b5d775ddec23"
down_revision = "705410a724b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("beneficiary_fraud_check", sa.Column("updatedAt", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("beneficiary_fraud_check", "updatedAt")
