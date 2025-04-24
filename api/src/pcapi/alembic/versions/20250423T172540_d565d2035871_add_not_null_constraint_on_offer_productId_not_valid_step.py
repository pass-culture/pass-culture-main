"""Add NOT NULL constraint on "offer.productId" NOT VALID step"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d565d2035871"
down_revision = "e9cf3954ed3b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offer" DROP CONSTRAINT IF EXISTS "check_offer_linked_to_product_constraint";
        ALTER TABLE "offer" ADD CONSTRAINT "check_offer_linked_to_product_constraint" CHECK (
            ("productId" IS NOT NULL AND description IS NULL AND "durationMinutes" IS NULL AND ("jsonData" IS NULL OR "jsonData"::text = 'null'))
            OR "productId" IS NULL
        ) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("check_offer_linked_to_product_constraint", table_name="offer")
