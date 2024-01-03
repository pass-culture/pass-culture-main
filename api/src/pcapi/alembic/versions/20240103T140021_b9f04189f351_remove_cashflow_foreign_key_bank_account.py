"""Remove Cashflow.bankAccount foreignkey
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b9f04189f351"
down_revision = "48e05c743111"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_cashflow_bankAccountId", table_name="cashflow")
    op.drop_constraint("cashflow_bankAccountId_fkey", "cashflow", type_="foreignkey")
    op.drop_column("cashflow", "bankAccountId")


def downgrade() -> None:
    op.add_column("cashflow", sa.Column("bankAccountId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key("cashflow_bankAccountId_fkey", "cashflow", "bank_information", ["bankAccountId"], ["id"])
    op.create_index("ix_cashflow_bankAccountId", "cashflow", ["bankAccountId"], unique=False)
