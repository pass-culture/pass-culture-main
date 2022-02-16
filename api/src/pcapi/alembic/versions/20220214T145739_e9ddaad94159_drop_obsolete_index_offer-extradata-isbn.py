"""drop obsolete index on offer.extraData.isbn
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e9ddaad94159"
down_revision = "e9ddaad94158"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP INDEX IF EXISTS offer_expr_idx;")


def downgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS offer_expr_idx ON offer (("extraData" ->> 'isbn'))
        """
    )
