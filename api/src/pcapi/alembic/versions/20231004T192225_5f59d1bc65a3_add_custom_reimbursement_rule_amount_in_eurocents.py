"""Add `custom_reimbursement_rule.amountInEuroCents` column"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5f59d1bc65a3"
down_revision = "c5009a056b16"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("custom_reimbursement_rule", sa.Column("amountInEuroCents", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("custom_reimbursement_rule", "amountInEuroCents")
