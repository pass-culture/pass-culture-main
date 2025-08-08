"""Create unaccented index on artist.artist_alias_name"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fe62e0063fc8"
down_revision = "ec3a564e0f35"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            ix_artist_alias_trgm_unaccent_name ON public.artist_alias
            USING gin (immutable_unaccent(artist_alias_name) gin_trgm_ops);
            """
        )

        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_artist_alias_trgm_unaccent_name",
            table_name="artist_alias",
            postgresql_concurrently=True,
            if_exists=True,
        )
