"""Index creation for stock.offererAddressId"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "edb5d745e273"
down_revision = "e0ade941956f"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
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


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_stock_offererAddressId",
            table_name="stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
