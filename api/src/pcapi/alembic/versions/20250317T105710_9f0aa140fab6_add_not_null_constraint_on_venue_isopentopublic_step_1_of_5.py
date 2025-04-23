"""Add NOT NULL constraint on "venue.isOpenToPublic" (step 1 of 5)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9f0aa140fab6"
down_revision = "05426e835a6b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_isOpenToPublic_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_isOpenToPublic_not_null_constraint" CHECK ("isOpenToPublic" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venue_isOpenToPublic_not_null_constraint", table_name="venue")
