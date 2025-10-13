"""Recreate index: ix_unique_offerer_address_per_label"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "59500baa64f3"
down_revision = "419a69945828"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_unique_offerer_address_per_label",
            "offerer_address",
            ["offererId", "addressId", "label"],
            unique=True,
            postgresql_where=sa.text('type IS NULL AND "venueId" IS NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_unique_offerer_address_per_label",
            table_name="offerer_address",
            postgresql_concurrently=True,
            if_exists=True,
        )
