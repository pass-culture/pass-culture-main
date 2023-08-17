"""Add index on venue.bookingEmail
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b93e190cb690"
down_revision = "60d79ba5b52a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # # We need to commit the transaction, because `CREATE INDEX
    # # CONCURRENTLY` cannot run inside a transaction.
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute("""CREATE INDEX CONCURRENTLY "idx_venue_bookingEmail" ON venue ("bookingEmail")""")
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    # We need to commit the transaction, because `DROP INDEX
    # CONCURRENTLY` cannot run inside a transaction.
    op.execute("COMMIT")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_bookingEmail";""")
