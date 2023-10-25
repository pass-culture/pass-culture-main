"""Remove `custom_reimbursement_rule.amountInEurocents` column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "55e87bc5d320"
down_revision = "80ee25f3632d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("custom_reimbursement_rule", "amountInEuroCents")


def downgrade() -> None:
    op.add_column(
        "custom_reimbursement_rule", sa.Column("amountInEuroCents", sa.INTEGER(), autoincrement=False, nullable=True)
    )
