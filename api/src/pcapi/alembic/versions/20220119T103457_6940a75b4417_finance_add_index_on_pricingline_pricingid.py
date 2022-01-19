"""Add index on pricing_line.pricingId"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "6940a75b4417"
down_revision = "e07f81517c8a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_pricing_line_pricingId" ON pricing_line ("pricingId")
        """
    )
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    # The index is very long to create, we really don't want to remove
    # it even if we rollback.
    pass
