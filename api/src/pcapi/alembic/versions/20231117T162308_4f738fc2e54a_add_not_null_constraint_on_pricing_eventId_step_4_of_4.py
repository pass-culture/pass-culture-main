"""Add NOT NULL constraint on "pricing.eventId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4f738fc2e54a"
down_revision = "c2bc7c46f7a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("pricing_eventId_not_null_constraint", table_name="pricing")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "pricing" ADD CONSTRAINT "pricing_eventId_not_null_constraint" CHECK ("eventId" IS NOT NULL) NOT VALID"""
    )
