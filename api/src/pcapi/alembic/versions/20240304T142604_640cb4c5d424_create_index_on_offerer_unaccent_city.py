"""Create unaccented index on offerer.city"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "640cb4c5d424"
down_revision = "3a8d3a5b86b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_offerer_city",  # index was never used in production
            table_name="offerer",
            postgresql_using="gin",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_offerer_trgm_unaccent_city" ON public."offerer"
            USING gin (immutable_unaccent("city") gin_trgm_ops);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            index_name="ix_offerer_trgm_unaccent_city",
            table_name="offerer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            ix_offerer_city ON public.offerer
            USING gin (city public.gin_trgm_ops)
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
