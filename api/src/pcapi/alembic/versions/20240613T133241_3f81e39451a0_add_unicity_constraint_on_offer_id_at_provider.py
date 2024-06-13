"""
Add unicity constraint on the pair `idAtProvider` and `venueId` in `offer` table.
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3f81e39451a0"
down_revision = "3e180517700b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Should be executed quickly as we are using an index
    op.execute(
        """
        ALTER TABLE "offer" ADD CONSTRAINT "unique_idAtProvider_venueId" UNIQUE USING INDEX "venueId_idAtProvider_index"
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offer" DROP CONSTRAINT IF EXISTS "unique_idAtProvider_venueId";
        """
    )
    # `COMMIT` and isolation of the `CREATE UNIQUE INDEX CONCURRENTLY` command necessary since it cannot run in a transaction block
    op.execute("COMMIT;")
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "venueId_idAtProvider_index" ON offer ("venueId", "idAtProvider");
        """
    )
    op.execute("BEGIN;")
