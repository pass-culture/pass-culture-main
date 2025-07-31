"""Create unaccented index on artist.name"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bb820d57fd5b"
down_revision = "48519dd044d4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            ix_artist_trgm_unaccent_name ON public.artist
            USING gin (immutable_unaccent(name) gin_trgm_ops);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_artist_trgm_unaccent_name",
            table_name="artist",
            postgresql_concurrently=True,
            if_exists=True,
        )
