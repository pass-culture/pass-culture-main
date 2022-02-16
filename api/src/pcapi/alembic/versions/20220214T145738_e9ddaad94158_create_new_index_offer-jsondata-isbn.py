"""create new index on offer.jsonData.isbn
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e9ddaad94158"
down_revision = "e9ddaad94157"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS offer_isbn_idx ON offer (("jsonData" ->> 'isbn'))
        """
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS offer_isbn_idx;")
