"""Create unaccented index on offerer.name"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3a8d3a5b86b2"
down_revision = "c7a4d9de4c48"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_offerer_trgm_unaccent_name" ON public."offerer"
            USING gin (immutable_unaccent("name") gin_trgm_ops);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_offerer_trgm_unaccent_name",
            table_name="offerer",
            postgresql_concurrently=True,
            if_exists=True,
        )
