"""offerer_provider : create ix_offerer_provider_offererId (step 2 of 6)
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ed3641db9970"
down_revision = "3f4fef666cb4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offerer_provider_offererId"
        ON offerer_provider ("offererId")
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_offerer_provider_offererId"
        """
    )
