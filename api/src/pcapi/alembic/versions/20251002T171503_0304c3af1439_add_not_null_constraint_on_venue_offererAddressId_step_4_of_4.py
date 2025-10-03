"""Add NOT NULL constraint on "venue.offererAddressId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0304c3af1439"
down_revision = "a8bd8e8f8db8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("venue_offererAddressId_not_null_constraint", table_name="venue")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_offererAddressId_not_null_constraint" CHECK ("offererAddressId" IS NOT NULL) NOT VALID"""
    )
