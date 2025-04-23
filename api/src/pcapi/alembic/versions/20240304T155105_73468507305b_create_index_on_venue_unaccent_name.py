"""Create unaccented index on venue.name"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "73468507305b"
down_revision = "640cb4c5d424"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_venue_trgm_unaccent_name" ON public."venue"
            USING gin (immutable_unaccent("name") gin_trgm_ops);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_venue_trgm_unaccent_name",
            table_name="venue",
            postgresql_concurrently=True,
            if_exists=True,
        )
