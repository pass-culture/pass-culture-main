"""remove_trgm_index_for_user_firstname_and_lastname
"""
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "77555a4c81c0"
down_revision = "ee836a8a56e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "idx_user_trgm_first_name"
        """
    )
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "idx_user_trgm_last_name"
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_trgm_first_name
        ON public.user
        USING gin ("firstName" public.gin_trgm_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_trgm_last_name
        ON public.user
        USING gin ("lastName" public.gin_trgm_ops)
        """
    )
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")
