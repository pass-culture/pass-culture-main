"""Create partial index "ix_stock_offerId_beginningDatetime_available" on "stock" table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "83175286f95b"
down_revision = "635a4b23fc44"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.create_index(
            "ix_stock_offerId_beginningDatetime_available",
            "stock",
            ["offerId", "beginningDatetime"],
            unique=False,
            postgresql_where=sa.text(
                '"isSoftDeleted" IS NOT TRUE AND (quantity IS NULL OR quantity > "dnBookedQuantity")'
            ),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.drop_index(
            "ix_stock_offerId_beginningDatetime_available",
            table_name="stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
