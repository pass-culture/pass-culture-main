"""
Add unique index on offerId/idAtProviders in stock table
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f11f5d888f80"
down_revision = "20579712cf72"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "unique_ix_offer_id_id_at_providers" ON stock ("offerId", "idAtProviders");
        """
    )
    op.execute("BEGIN;")


def downgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "unique_ix_offer_id_id_at_providers";
        """
    )
    op.execute("BEGIN;")
