"""create index ix_unique_offerer_address_per_label"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3d909838fadc"
down_revision = "56372cadc547"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_unique_offerer_address_per_label" on "offerer_address" ("offererId", "addressId", "label")"""
    )
    op.execute("BEGIN;")


def downgrade() -> None:
    op.execute("COMMIT;")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "ix_unique_offerer_address_per_label" """)
    op.execute("BEGIN;")
