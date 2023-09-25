"""Remove now unused indexes on offer and product isbn"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "12e531343466"
down_revision = "aae5aa12b1c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "offer_isbn_idx"
        """
    )
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "product_isbn_idx"
        """
    )


def downgrade() -> None:
    # Do not recreate indexes that are not used
    pass
