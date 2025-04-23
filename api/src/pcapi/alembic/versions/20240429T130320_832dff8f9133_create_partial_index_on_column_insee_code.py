"""Create unique index on Address.inseeCode where it's not null"""

from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "832dff8f9133"
down_revision = "abf890b12b43"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            "address",
            ["street", "inseeCode"],
            unique=True,
            postgresql_where=sa.text('"street" IS NOT NULL and "inseeCode" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            table_name="address",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
