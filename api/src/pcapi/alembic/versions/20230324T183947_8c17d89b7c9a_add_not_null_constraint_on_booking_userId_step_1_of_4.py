"""Add NOT NULL constraint on "booking.userId" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8c17d89b7c9a"
down_revision = "aa37244acc4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "booking" DROP CONSTRAINT IF EXISTS "booking_userId_not_null_constraint";
        ALTER TABLE "booking" ADD CONSTRAINT "booking_userId_not_null_constraint" CHECK ("userId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("booking_userId_not_null_constraint", table_name="booking")
