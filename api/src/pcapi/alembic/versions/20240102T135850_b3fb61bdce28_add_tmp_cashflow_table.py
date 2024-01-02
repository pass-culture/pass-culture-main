"""Add tmp_cashflow and tmp_invoice_cashflow table
"""
from alembic import op
import sqlalchemy as sa

from pcapi.core.finance.models import CashflowStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b3fb61bdce28"
down_revision = "223b14fd3dd8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tmp_cashflow",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", MagicEnum(CashflowStatus), nullable=False),
        sa.Column("bankAccountId", sa.BigInteger(), nullable=True),
        sa.Column("bankInformationId", sa.BigInteger(), nullable=True),
        sa.Column("reimbursementPointId", sa.BigInteger(), nullable=False),
        sa.Column("batchId", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.CheckConstraint('("amount" != 0)', name="non_zero_amount_check"),
        sa.ForeignKeyConstraint(
            ["bankAccountId"],
            ["bank_account.id"],
        ),
        sa.ForeignKeyConstraint(
            ["batchId"],
            ["cashflow_batch.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reimbursementPointId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tmp_cashflow_bankAccountId"), "tmp_cashflow", ["bankAccountId"], unique=False)
    op.create_index(op.f("ix_tmp_cashflow_batchId"), "tmp_cashflow", ["batchId"], unique=False)
    op.create_index(
        op.f("ix_tmp_cashflow_reimbursementPointId"), "tmp_cashflow", ["reimbursementPointId"], unique=False
    )
    op.create_index(op.f("ix_tmp_cashflow_status"), "tmp_cashflow", ["status"], unique=False)
    op.create_table(
        "tmp_invoice_cashflow",
        sa.Column("invoiceId", sa.BigInteger(), nullable=False),
        sa.Column("cashflowId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cashflowId"],
            ["tmp_cashflow.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invoiceId"],
            ["tmp_invoice.id"],
        ),
        sa.PrimaryKeyConstraint("invoiceId", "cashflowId", name="unique_invoice_cashflow_association"),
    )
    op.create_index(op.f("ix_tmp_invoice_cashflow_cashflowId"), "tmp_invoice_cashflow", ["cashflowId"], unique=False)
    op.create_index(op.f("ix_tmp_invoice_cashflow_invoiceId"), "tmp_invoice_cashflow", ["invoiceId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tmp_invoice_cashflow_invoiceId"), table_name="tmp_invoice_cashflow")
    op.drop_index(op.f("ix_tmp_invoice_cashflow_cashflowId"), table_name="tmp_invoice_cashflow")
    op.drop_table("tmp_invoice_cashflow")
    op.drop_index(op.f("ix_tmp_cashflow_status"), table_name="tmp_cashflow")
    op.drop_index(op.f("ix_tmp_cashflow_reimbursementPointId"), table_name="tmp_cashflow")
    op.drop_index(op.f("ix_tmp_cashflow_batchId"), table_name="tmp_cashflow")
    op.drop_index(op.f("ix_tmp_cashflow_bankAccountId"), table_name="tmp_cashflow")
    op.drop_table("tmp_cashflow")
