"""Add NOT NULL constraint on "fraudulent_booking_tag.venueId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "869c61cd3a23"
down_revision = "738731d5c09c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("fraudulent_booking_tag_venueId_not_null_constraint", table_name="fraudulent_booking_tag")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "fraudulent_booking_tag" ADD CONSTRAINT "fraudulent_booking_tag_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID"""
    )
