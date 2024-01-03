""" Add "bankAccountId" foreign key to "invoice" table."""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ea0a25aef628"
down_revision = "16ebdf83377e"
branch_labels = None
depends_on = None

FOREIGN_KEY_NAME = "invoice_BankAccountId_fkey"


def upgrade() -> None:
    op.add_column("invoice", sa.Column("bankAccountId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_invoice_bankAccountId"), "invoice", ["bankAccountId"], unique=False)
    op.create_foreign_key(FOREIGN_KEY_NAME, "invoice", "bank_account", ["bankAccountId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(FOREIGN_KEY_NAME, "invoice", type_="foreignkey")
    op.drop_index(op.f("ix_invoice_bankAccountId"), table_name="invoice")
    op.drop_column("invoice", "bankAccountId")
