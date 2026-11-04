"""Add NOT NULL constraint on "venue.validationStatus" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "07f33b4d4b2e"
down_revision = "37ece4493586"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("venue_validationStatus_not_null_constraint", table_name="venue")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_validationStatus_not_null_constraint" CHECK ("validationStatus" IS NOT NULL) NOT VALID"""
    )
