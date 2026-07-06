"""Add NOT NULL constraint on "venue.activity" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8499f0606e34"
down_revision = "1b33a3a686da"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("venue_activity_not_null_constraint", table_name="venue")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_activity_not_null_constraint" CHECK ("activity" IS NOT NULL) NOT VALID"""
    )
