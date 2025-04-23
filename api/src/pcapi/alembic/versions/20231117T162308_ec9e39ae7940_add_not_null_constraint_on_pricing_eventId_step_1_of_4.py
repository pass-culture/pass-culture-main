"""Add NOT NULL constraint on "pricing.eventId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ec9e39ae7940"
down_revision = "6993f48deb4b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "pricing" DROP CONSTRAINT IF EXISTS "pricing_eventId_not_null_constraint";
        ALTER TABLE "pricing" ADD CONSTRAINT "pricing_eventId_not_null_constraint" CHECK ("eventId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("pricing_eventId_not_null_constraint", table_name="pricing")
