"""drop obsolete index on product.extraData.isbn
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e9ddaad94160"
down_revision = "e9ddaad94159"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP INDEX IF EXISTS product_expr_idx;")


def downgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS product_expr_idx ON product (("extraData" ->> 'isbn'))
        """
    )
