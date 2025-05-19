"""Index creation for offer.offererAdressId"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0dc3123e5ede"
down_revision = "edb5d745e273"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_offer_offererAddressId",
            "offer",
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
            "ix_offer_offererAddressId",
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
            postgresql_where=sa.text('"offererAddressId" IS NOT NULL'),
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
