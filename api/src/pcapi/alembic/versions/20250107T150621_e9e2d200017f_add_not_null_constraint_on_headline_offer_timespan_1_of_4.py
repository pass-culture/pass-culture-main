"""
Add NOT NULL constraint on "headline_offer.timespan" (step 1 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e9e2d200017f"
down_revision = "a8d2c442cc67"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "headline_offer" DROP CONSTRAINT IF EXISTS "timespan_not_null_constraint";
        ALTER TABLE "headline_offer" ADD CONSTRAINT "timespan_not_null_constraint" CHECK ("timespan" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS timespan_not_null_constraint")
