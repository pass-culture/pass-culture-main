"""Make Cashflow.bankAccountId nullable
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "71effb72345c"
down_revision = "ea0a25aef628"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("cashflow", "bankAccountId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    # Nothing to downgrade, the column is being removed in a post migration
    pass
