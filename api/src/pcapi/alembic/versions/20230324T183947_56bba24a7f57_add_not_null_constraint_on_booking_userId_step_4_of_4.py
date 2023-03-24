"""Add NOT NULL constraint on "booking.userId" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "56bba24a7f57"
down_revision = "558feec91836"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("booking_userId_not_null_constraint", table_name="booking")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "booking" ADD CONSTRAINT "booking_userId_not_null_constraint" CHECK ("userId" IS NOT NULL) NOT VALID"""
    )
