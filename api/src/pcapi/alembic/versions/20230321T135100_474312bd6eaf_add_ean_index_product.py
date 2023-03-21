"""add_ean_index_product
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "474312bd6eaf"
down_revision = "061957688845"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS product_ean_idx
        ON product
        USING btree ((("jsonData" ->> 'ean'::text)));
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "product_ean_idx"
        """
    )
