"""Create index on address.city (similar to deprecated offerer.city)"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "332bf1038090"
down_revision = "ae91ad1d3d2b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_address_trgm_unaccent_city",
            "address",
            [sa.text("immutable_unaccent(city)")],
            postgresql_using="gin",
            postgresql_ops={"immutable_unaccent(city)": "gin_trgm_ops"},
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_address_trgm_unaccent_city", table_name="address", postgresql_concurrently=True, if_exists=True
        )
