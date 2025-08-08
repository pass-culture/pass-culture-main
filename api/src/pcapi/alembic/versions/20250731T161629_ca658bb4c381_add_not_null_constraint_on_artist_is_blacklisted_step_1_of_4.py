"""Add NOT NULL constraint on "artist.is_blacklisted" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ca658bb4c381"
down_revision = "bb820d57fd5b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "artist" DROP CONSTRAINT IF EXISTS "artist_is_blacklisted_not_null_constraint";
        ALTER TABLE "artist" ADD CONSTRAINT "artist_is_blacklisted_not_null_constraint" CHECK ("is_blacklisted" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("artist_is_blacklisted_not_null_constraint", table_name="artist")
