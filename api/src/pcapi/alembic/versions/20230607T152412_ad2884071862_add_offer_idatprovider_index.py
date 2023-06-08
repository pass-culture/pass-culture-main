"""Add index on offer.idAtProvider
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ad2884071862"
down_revision = "36e81e25b30b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # # We need to commit the transaction, because `CREATE INDEX
    # # CONCURRENTLY` cannot run inside a transaction.
    op.execute("COMMIT")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "offer_idAtProvider" ON offer ("idAtProvider")""")


def downgrade() -> None:
    # We need to commit the transaction, because `DROP INDEX
    # CONCURRENTLY` cannot run inside a transaction.
    op.execute("COMMIT")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "offer_idAtProvider";""")
