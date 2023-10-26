"""
create index on last validation author fk on "offer" table
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a98c6b643561"
down_revision = "6025fbc18ebb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_lastValidationAuthorUserId"
        ON offer("lastValidationAuthorUserId")
        WHERE "lastValidationAuthorUserId" IS NOT NULL;
    """
    )


def downgrade() -> None:
    op.drop_index("idx_offer_lastValidationAuthorUserId", "offer")
