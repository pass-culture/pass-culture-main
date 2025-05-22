"""delete_stock_offereraddress"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0a17873525e7"
down_revision = "01840c8231e3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_stock_offererAddressId",
            table_name="stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
    op.drop_constraint("stock_offererAddressId_fkey", "stock", type_="foreignkey")
    op.drop_column("stock", "offererAddressId")


def downgrade() -> None:
    op.add_column("stock", sa.Column("offererAddressId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key(
        "stock_offererAddressId_fkey",
        "stock",
        "offerer_address",
        ["offererAddressId"],
        ["id"],
        postgresql_not_valid=True,
    )
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_stock_offererAddressId",
            "stock",
            ["offererAddressId"],
            unique=False,
            postgresql_concurrently=True,
            postgresql_where=sa.text('"offererAddressId" IS NOT NULL'),
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
