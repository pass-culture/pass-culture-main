"""Remove unique constraint on bankInformation.offererId
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9b8702ecd055"
down_revision = "76109536b81c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""DROP INDEX IF EXISTS "ix_bank_information_offererId";""")
    op.execute("COMMIT")
    op.execute(
        """CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_bank_information_offererId" ON bank_information("offererId") WHERE "offererId" IS NOT NULL;"""
    )


def downgrade() -> None:
    op.execute("""DROP INDEX IF EXISTS "ix_bank_information_offererId";""")
    op.execute("COMMIT")
    op.execute(
        """CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_bank_information_offererId" ON bank_information("offererId");"""
    )
