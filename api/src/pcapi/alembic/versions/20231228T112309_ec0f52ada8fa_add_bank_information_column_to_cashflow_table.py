"""
Rename bankAccountId to bankInformationId 1st step: Add "bankInformationId" to "cashflow" table
"""
from alembic import op
import sqlalchemy as sa


revision = "ec0f52ada8fa"
down_revision = "a1500ef1ad7c"
branch_labels = None
depends_on = None

FOREIGN_KEY_NAME = "cashflow_bankInformationId_fkey"


def upgrade() -> None:
    op.add_column("cashflow", sa.Column("bankInformationId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_cashflow_bankInformationId"), "cashflow", ["bankInformationId"], unique=False)
    op.create_foreign_key(FOREIGN_KEY_NAME, "cashflow", "bank_information", ["bankInformationId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(FOREIGN_KEY_NAME, "cashflow", type_="foreignkey")
    op.drop_index(op.f("ix_cashflow_bankInformationId"), table_name="cashflow")
    op.drop_column("cashflow", "bankInformationId")
