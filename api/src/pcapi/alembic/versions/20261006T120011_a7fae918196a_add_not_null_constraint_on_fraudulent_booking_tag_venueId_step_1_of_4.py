"""Add NOT NULL constraint on "fraudulent_booking_tag.venueId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a7fae918196a"
down_revision = "2a8c112f9ca4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "fraudulent_booking_tag" DROP CONSTRAINT IF EXISTS "fraudulent_booking_tag_venueId_not_null_constraint";
        ALTER TABLE "fraudulent_booking_tag" ADD CONSTRAINT "fraudulent_booking_tag_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("fraudulent_booking_tag_venueId_not_null_constraint", table_name="fraudulent_booking_tag")
