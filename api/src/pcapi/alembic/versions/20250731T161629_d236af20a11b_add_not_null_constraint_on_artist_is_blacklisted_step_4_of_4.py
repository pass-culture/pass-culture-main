"""Add NOT NULL constraint on "artist.is_blacklisted" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d236af20a11b"
down_revision = "3d913bae7e96"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("artist_is_blacklisted_not_null_constraint", table_name="artist")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "artist" ADD CONSTRAINT "artist_is_blacklisted_not_null_constraint" CHECK ("is_blacklisted" IS NOT NULL) NOT VALID"""
    )
