"""
add price index on collective_stock
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e82695d3ec03"
down_revision = "c8e741468d2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_collective_stock_price"),
            "collective_stock",
            ["price"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_collective_stock_price"),
            table_name="collective_stock",
            if_exists=True,
            postgresql_concurrently=True,
        )
