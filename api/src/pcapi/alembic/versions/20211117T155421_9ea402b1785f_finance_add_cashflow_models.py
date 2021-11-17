"""Add Cashflow and related models."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "9ea402b1785f"
down_revision = "8794f331080c"
branch_labels = None
depends_on = None


def upgrade():
    import pcapi.core.finance.models as finance_models
    import pcapi.utils.db as db_utils

    op.create_table(
        "cashflow_batch",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("cutoff", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cutoff"),
    )
    op.create_table(
        "cashflow",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", db_utils.MagicEnum(finance_models.CashflowStatus), nullable=False),
        sa.Column("bankAccountId", sa.BigInteger(), nullable=False),
        sa.Column("batchId", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "transactionId", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.CheckConstraint('("amount" != 0)', name="non_zero_amount_check"),
        sa.ForeignKeyConstraint(
            ["bankAccountId"],
            ["bank_information.id"],
        ),
        sa.ForeignKeyConstraint(
            ["batchId"],
            ["cashflow_batch.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transactionId"),
    )
    op.create_index(op.f("ix_cashflow_bankAccountId"), "cashflow", ["bankAccountId"], unique=False)
    op.create_index(op.f("ix_cashflow_status"), "cashflow", ["status"], unique=False)
    op.create_table(
        "cashflow_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cashflowId", sa.BigInteger(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("statusBefore", db_utils.MagicEnum(finance_models.CashflowStatus), nullable=False),
        sa.Column("statusAfter", db_utils.MagicEnum(finance_models.CashflowStatus), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=True),
        sa.ForeignKeyConstraint(
            ["cashflowId"],
            ["cashflow.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cashflow_log_cashflowId"), "cashflow_log", ["cashflowId"], unique=False)
    op.create_table(
        "cashflow_pricing",
        sa.Column("cashflowId", sa.BigInteger(), nullable=False),
        sa.Column("pricingId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cashflowId"],
            ["cashflow.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pricingId"],
            ["pricing.id"],
        ),
        sa.PrimaryKeyConstraint("cashflowId", "pricingId"),
    )
    op.create_unique_constraint("unique_cashflow_pricing_association", "cashflow_pricing", ["cashflowId", "pricingId"])
    op.create_index(op.f("ix_cashflow_pricing_cashflowId"), "cashflow_pricing", ["cashflowId"], unique=False)
    op.create_index(op.f("ix_cashflow_pricing_pricingId"), "cashflow_pricing", ["pricingId"], unique=False)


def downgrade():
    op.drop_table("cashflow_pricing")
    op.drop_table("cashflow_log")
    op.drop_table("cashflow")
    op.drop_table("cashflow_batch")
