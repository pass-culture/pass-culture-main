"""Add unique index with nulls not distinct on Address table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c1eaf46afc44"
down_revision = "c2282b67bd45"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_unique_complete_address_with_nulls_not_distinct" on "address" ("banId", "inseeCode", "street", "postalCode", "city", "latitude", "longitude") NULLS NOT DISTINCT """
    )
    op.execute("BEGIN;")


def downgrade() -> None:
    op.execute("COMMIT;")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "ix_unique_complete_address_with_nulls_not_distinct" """)
    op.execute("BEGIN;")
