"""Add index to the stock_screening table"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6942be91607f"
down_revision = "e1856b6ce435"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_screening_stockId"),
            "screening",
            ["stockId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_screening_stockId"),
            table_name="screening",
            postgresql_concurrently=True,
            if_exists=True,
        )
