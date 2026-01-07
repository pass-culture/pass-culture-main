"""Drop CashflowLog table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "776aaf4893d0"
down_revision = "f5595415f44e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("cashflow_log")


def downgrade() -> None:
    op.create_table(
        "cashflow_log",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("cashflowId", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "timestamp", postgresql.TIMESTAMP(), server_default=sa.text("now()"), autoincrement=False, nullable=False
        ),
        sa.Column("statusBefore", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column("statusAfter", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["cashflowId"], ["cashflow.id"], name=op.f("cashflow_log_cashflowId_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("cashflow_log_pkey")),
    )
    op.create_index(op.f("ix_cashflow_log_cashflowId"), "cashflow_log", ["cashflowId"], unique=False)
