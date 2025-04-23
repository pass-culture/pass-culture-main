"""Drop Address.banId unique constraint"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3fe28059d41c"
down_revision = "1f3bc7f32c9f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE address DROP CONSTRAINT IF EXISTS "address_banId_key" """)
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_unique_address_per_banid",
            table_name="address",
            if_exists=True,
            postgresql_where='("banId" IS NOT NULL)',
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_unique_address_per_banid",
            "address",
            ["banId"],
            unique=True,
            if_not_exists=True,
            postgresql_where='("banId" IS NOT NULL)',
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
