"""Create unaccented index on venue.publicName"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "23fa7b1b692e"
down_revision = "73468507305b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_venue_trgm_unaccent_public_name" ON public."venue"
            USING gin (immutable_unaccent("publicName") gin_trgm_ops);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_venue_trgm_unaccent_public_name",
            table_name="venue",
            postgresql_concurrently=True,
            if_exists=True,
        )
