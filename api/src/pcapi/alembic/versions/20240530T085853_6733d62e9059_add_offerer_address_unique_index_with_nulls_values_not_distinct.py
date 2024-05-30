"""Add unique index on OffererAddress that supports not distinct nulls label values
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6733d62e9059"
down_revision = "2e66d0e6d190"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_unique_offerer_address_per_label_even_with_nulls_values" on "offerer_address" ("offererId", "addressId", "label") NULLS NOT DISTINCT """
    )
    op.execute("BEGIN;")


def downgrade() -> None:
    op.execute("COMMIT;")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "ix_unique_offerer_address_per_label_even_with_nulls_values" """)
    op.execute("BEGIN;")
