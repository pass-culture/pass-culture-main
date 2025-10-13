"""Add NOT NULL constraint on "venue.publicName" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c3d5fb8de1e6"
down_revision = "ae9151369f8d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_publicName_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_publicName_not_null_constraint" CHECK ("publicName" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venue_publicName_not_null_constraint", table_name="venue")
