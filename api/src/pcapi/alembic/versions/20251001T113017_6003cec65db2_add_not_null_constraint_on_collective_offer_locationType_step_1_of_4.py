"""Add NOT NULL constraint on "collective_offer.locationType" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6003cec65db2"
down_revision = "6d61c431f11b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer" DROP CONSTRAINT IF EXISTS "collective_offer_locationType_not_null_constraint";
        ALTER TABLE "collective_offer" ADD CONSTRAINT "collective_offer_locationType_not_null_constraint" CHECK ("locationType" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_locationType_not_null_constraint", table_name="collective_offer")
