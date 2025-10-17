"""Drop index on offerer.city"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b75ece6e9925"
down_revision = "fc980c1d0445"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_offerer_trgm_unaccent_city"),
            table_name="offerer",
            if_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_offerer_trgm_unaccent_city",
            "offerer",
            [sa.text("immutable_unaccent(city)")],
            postgresql_using="gin",
            postgresql_ops={"immutable_unaccent(city)": "gin_trgm_ops"},
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
