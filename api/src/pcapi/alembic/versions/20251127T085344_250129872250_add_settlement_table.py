"""Add Settlement, SettlementBatch and InvoiceSettlement tables"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.finance.models import SettlementStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "250129872250"
down_revision = "345f5470056e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "settlement_batch",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("label"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "settlement",
        sa.Column("settlementDate", sa.Date(), nullable=False),
        sa.Column("dateImported", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("dateRejected", sa.DateTime(), nullable=True),
        sa.Column("externalSettlementId", sa.Text(), nullable=False),
        sa.Column("bankAccountId", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("status", MagicEnum(SettlementStatus), nullable=False),
        sa.Column("batchId", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["bankAccountId"],
            ["bank_account.id"],
        ),
        sa.ForeignKeyConstraint(
            ["batchId"],
            ["settlement_batch.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("externalSettlementId", "bankAccountId", name="unique_cegid_settlement_id_bank_account_id"),
    )
    op.create_index(op.f("ix_settlement_bankAccountId"), "settlement", ["bankAccountId"], unique=False)
    op.create_index(op.f("ix_settlement_batchId"), "settlement", ["batchId"], unique=False)

    op.create_table(
        "invoice_settlement",
        sa.Column("invoiceId", sa.BigInteger(), nullable=False),
        sa.Column("settlementId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["invoiceId"],
            ["invoice.id"],
        ),
        sa.ForeignKeyConstraint(
            ["settlementId"],
            ["settlement.id"],
        ),
        sa.PrimaryKeyConstraint("invoiceId", "settlementId", name="unique_invoice_settlement_association"),
    )
    op.create_index(op.f("ix_invoice_settlement_invoiceId"), "invoice_settlement", ["invoiceId"], unique=False)
    op.create_index(op.f("ix_invoice_settlement_settlementId"), "invoice_settlement", ["settlementId"], unique=False)


def downgrade() -> None:
    op.drop_table("invoice_settlement")
    op.drop_table("settlement")
    op.drop_table("settlement_batch")
