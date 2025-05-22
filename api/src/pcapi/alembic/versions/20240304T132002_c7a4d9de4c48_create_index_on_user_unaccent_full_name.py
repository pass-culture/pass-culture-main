"""Create unaccented index on user.firstName + user.lastName"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c7a4d9de4c48"
down_revision = "1be3db2bd7b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE OR REPLACE FUNCTION public.immutable_unaccent(text)
                RETURNS text
                LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
            $$
                SELECT public.unaccent('public.unaccent', $1)
            $$
            ;
            """
        )
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_user_trgm_unaccent_full_name" ON public."user"
            USING gin (immutable_unaccent("firstName" || ' ' || "lastName") gin_trgm_ops);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_user_trgm_unaccent_full_name",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute("""DROP FUNCTION IF EXISTS public.immutable_unaccent;""")
