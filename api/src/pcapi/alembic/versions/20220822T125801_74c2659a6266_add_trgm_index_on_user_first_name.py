"""add_trgm_index_on_user_first_name
"""
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "74c2659a6266"
down_revision = "76d1434f787d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_trgm_first_name
        ON public.user
        USING gin ("firstName" public.gin_trgm_ops)
        """
    )
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "idx_user_trgm_last_name"
        """
    )
