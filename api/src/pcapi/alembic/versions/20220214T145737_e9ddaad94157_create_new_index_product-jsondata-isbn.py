"""create new index on product.jsonData.isbn
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e9ddaad94157"
down_revision = "e9ddaad94156"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS product_isbn_idx ON product (("jsonData" ->> 'isbn'))
        """
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS product_isbn_idx;")
