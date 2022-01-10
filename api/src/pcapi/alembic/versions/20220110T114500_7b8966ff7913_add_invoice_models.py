"""Add Invoice-related models"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "7b8966ff7913"
down_revision = "1e92f54267a9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "invoice_cashflow",
        sa.Column("invoiceId", sa.BigInteger(), nullable=False),
        sa.Column("cashflowId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cashflowId"],
            ["cashflow.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invoiceId"],
            ["invoice.id"],
        ),
        sa.PrimaryKeyConstraint("invoiceId", "cashflowId"),
        sa.UniqueConstraint("invoiceId", "cashflowId", name="unique_invoice_cashflow_association"),
    )
    op.create_index(op.f("ix_invoice_cashflow_cashflowId"), "invoice_cashflow", ["cashflowId"], unique=False)
    op.create_index(op.f("ix_invoice_cashflow_invoiceId"), "invoice_cashflow", ["invoiceId"], unique=False)
    op.create_table(
        "invoice_line",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("invoiceId", sa.BigInteger(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("group", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("contribution_amount", sa.Integer(), nullable=False),
        sa.Column("reimbursed_amount", sa.Integer(), nullable=False),
        sa.Column("rate", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.ForeignKeyConstraint(
            ["invoiceId"],
            ["invoice.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_line_invoiceId"), "invoice_line", ["invoiceId"], unique=False)


def downgrade():
    op.drop_table("invoice_line")
    op.drop_table("invoice_cashflow")
