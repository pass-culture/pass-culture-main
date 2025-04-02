"""Add NOT NULL constraint on "collective_offer.formats" (step 1 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ca5d826f6db4"
down_revision = "0fbfa18bdad2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer" DROP CONSTRAINT IF EXISTS "collective_offer_formats_not_null_constraint";
        ALTER TABLE "collective_offer" ADD CONSTRAINT "collective_offer_formats_not_null_constraint" CHECK ("formats" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_formats_not_null_constraint", table_name="collective_offer")
