"""
create index on last validation author fk on "collective_offer_template" table
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "80ee25f3632d"
down_revision = "00d812005230"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_collective_offer_template_lastValidationAuthorUserId"
        ON collective_offer_template("lastValidationAuthorUserId")
        WHERE "lastValidationAuthorUserId" IS NOT NULL;
    """
    )


def downgrade() -> None:
    op.drop_index("idx_collective_offer_template_lastValidationAuthorUserId", "collective_offer_template")
