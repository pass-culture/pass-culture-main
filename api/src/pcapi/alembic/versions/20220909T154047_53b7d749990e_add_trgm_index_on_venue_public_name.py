"""add_trgm_index_on_venue_public_name
"""
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "53b7d749990e"
down_revision = "abc92addfaeb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_venue_trgm_public_name
        ON venue
        USING gin ("publicName" public.gin_trgm_ops)
        """
    )
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_trgm_public_name"
        """
    )
