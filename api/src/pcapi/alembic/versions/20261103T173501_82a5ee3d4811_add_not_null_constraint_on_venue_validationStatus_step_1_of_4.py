"""Add NOT NULL constraint on "venue.validationStatus" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "82a5ee3d4811"
down_revision = "0f80fa0efa85"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_validationStatus_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_validationStatus_not_null_constraint" CHECK ("validationStatus" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venue_validationStatus_not_null_constraint", table_name="venue")
