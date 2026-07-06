"""Add NOT NULL constraint on "venue.activity" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "792091afeb3d"
down_revision = "6326d7f881b3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_activity_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_activity_not_null_constraint" CHECK ("activity" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venue_activity_not_null_constraint", table_name="venue")
