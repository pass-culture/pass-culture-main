"""create ix_artist_offer_link_offer_id index on artist_offer_link table"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f5595415f44e"
down_revision = "e1dc3abc6f31"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='45s'")
        op.execute("SET SESSION lock_timeout='10s'")
        op.create_index(
            op.f("ix_artist_offer_link_offer_id"),
            "artist_offer_link",
            ["offer_id"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
        op.execute(f"SET SESSION lock_timeout={settings.DATABASE_LOCK_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION lock_timeout='10s'")
        op.execute("SET SESSION statement_timeout='45s'")
        op.drop_index(
            op.f("ix_artist_offer_link_offer_id"),
            table_name="artist_offer_link",
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
        op.execute(f"SET SESSION lock_timeout={settings.DATABASE_LOCK_TIMEOUT}")
