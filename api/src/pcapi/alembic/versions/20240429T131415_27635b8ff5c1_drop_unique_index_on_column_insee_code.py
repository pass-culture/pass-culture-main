"""Drop unique index on Address.inseeCode"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "27635b8ff5c1"
down_revision = "832dff8f9133"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.drop_index(
            "ix_unique_address_per_street_and_insee_code",
            if_exists=True,
            table_name="address",
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.create_index(
            "ix_unique_address_per_street_and_insee_code",
            "address",
            ["street", "inseeCode"],
            if_not_exists=True,
            unique=True,
            postgresql_where='("banId" IS NULL)',
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
