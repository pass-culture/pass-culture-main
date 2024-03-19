"""
Remove non-zero constraint from amount column of Cashflow table
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "33c2838cfb4a"
down_revision = "4eeaf83a2a07"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
    op.drop_constraint(
        constraint_name="non_zero_amount_check",
        table_name="cashflow",
    )


def downgrade() -> None:
    op.create_check_constraint(
        constraint_name="non_zero_amount_check",
        table_name="cashflow",
        condition='("amount" != 0)',
        postgresql_not_valid=True,
    )
