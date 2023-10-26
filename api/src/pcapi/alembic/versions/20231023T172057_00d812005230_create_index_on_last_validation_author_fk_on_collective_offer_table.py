"""
create index on last validation author fk on "collective_offer" table
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "00d812005230"
down_revision = "a98c6b643561"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_collective_offer_lastValidationAuthorUserId"
        ON collective_offer("lastValidationAuthorUserId")
        WHERE "lastValidationAuthorUserId" IS NOT NULL;
    """
    )


def downgrade() -> None:
    op.drop_index("idx_collective_offer_lastValidationAuthorUserId", "collective_offer")
