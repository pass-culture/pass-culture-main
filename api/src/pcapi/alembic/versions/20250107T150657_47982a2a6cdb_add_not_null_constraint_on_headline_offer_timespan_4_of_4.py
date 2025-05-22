"""
Add NOT NULL constraint on "headline_offer.timespan" (step 4 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "47982a2a6cdb"
down_revision = "00e78149876e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('ALTER TABLE "headline_offer" DROP CONSTRAINT IF EXISTS "timespan_not_null_constraint";')


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "headline_offer" ADD CONSTRAINT "timespan_not_null_constraint" CHECK ("timespan" IS NOT NULL) NOT VALID;"""
    )
