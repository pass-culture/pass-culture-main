"""offerer_provider : create ix_offerer_provider_providerId (step 3 of 6)
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f67ecae084d5"
down_revision = "ed3641db9970"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offerer_provider_providerId"
        ON offerer_provider ("providerId")
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_offerer_provider_providerId"
        """
    )
