"""provider_api_key: create provider_id index (2/3)
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "00d3b5d28578"
down_revision = "a93013fc9866"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_api_key_providerId" ON api_key ("providerId")
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_api_key_providerId"
        """
    )
