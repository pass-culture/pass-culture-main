"""Create index: ix_wip_unique_offerer_address_when_label_is_not_null"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5ed5e8472e25"
down_revision = "7e4449c47348"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_wip_unique_offerer_address_when_label_is_not_null",
            "offerer_address",
            ["offererId", "addressId", "label", "type", "venueId"],
            unique=True,
            postgresql_where=sa.text("label IS NOT NULL"),
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_wip_unique_offerer_address_when_label_is_not_null",
            table_name="offerer_address",
            postgresql_concurrently=True,
            if_exists=True,
        )
