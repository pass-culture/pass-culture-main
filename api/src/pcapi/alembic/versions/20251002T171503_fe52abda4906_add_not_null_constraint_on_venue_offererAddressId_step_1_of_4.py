"""Add NOT NULL constraint on "venue.offererAddressId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fe52abda4906"
down_revision = "f3a44c36b40a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "venue_offererAddressId_not_null_constraint";
        ALTER TABLE "venue" ADD CONSTRAINT "venue_offererAddressId_not_null_constraint" CHECK ("offererAddressId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venue_offererAddressId_not_null_constraint", table_name="venue")
