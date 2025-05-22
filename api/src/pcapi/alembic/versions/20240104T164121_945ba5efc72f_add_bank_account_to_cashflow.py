"""Add "bankAccountId" fkey to "cashflow" table."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "945ba5efc72f"
down_revision = "b5ae2a2f7d59"
branch_labels = None
depends_on = None

FOREIGN_KEY_NAME = "cashflow_bankAccountId_fkey"
INDEX_NAME = "ix_cashflow_bankAccountId"


def upgrade() -> None:
    op.add_column("cashflow", sa.Column("bankAccountId", sa.BigInteger(), nullable=True))
    op.create_index(op.f(INDEX_NAME), "cashflow", ["bankAccountId"], unique=False)
    op.create_foreign_key(FOREIGN_KEY_NAME, "cashflow", "bank_account", ["bankAccountId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(FOREIGN_KEY_NAME, "cashflow", type_="foreignkey")
    op.drop_index(op.f(INDEX_NAME), table_name="cashflow")
    op.drop_column("cashflow", "bankAccountId")
