"""Create index on stock.idAtProviders"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d8a0801f62e2"
down_revision = "2a3cbc3aa996"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_stock_idAtProviders",
            "stock",
            ["idAtProviders"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_stock_idAtProviders",
            table_name="stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
