"""Add trigramme index on product name"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5505b2e9a2f4"
down_revision = "93508bd63958"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS product_trgm_name_idx
            ON product USING gin (name gin_trgm_ops)
        """)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""
            DROP INDEX CONCURRENTLY IF EXISTS product_trgm_name_idx
        """)
