"""index_educationel_offer
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "7f2d9876eb6e"
down_revision = "90c1a1eeeee0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
		SET SESSION statement_timeout = '300s'
		"""
    )
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_isEducational" ON offer ("isEducational")
        """
    )
    op.execute(
        f"""
           SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
           """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
		DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_isEducational"
		"""
    )
