"""Add NOT NULL constraint on "offer.productId" NOT VALID step"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d565d2035871"
down_revision = "122e253ad2d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Theses migrations have already been executed in staging and prod
    if settings.IS_PROD or settings.IS_STAGING:
        pass
    op.execute(
        """
        ALTER TABLE "offer" DROP CONSTRAINT IF EXISTS "check_offer_linked_to_product_constraint";
        ALTER TABLE "offer" ADD CONSTRAINT "check_offer_linked_to_product_constraint" CHECK (
            "productId" IS NULL
                OR (
                    description IS NULL
                    AND "durationMinutes" IS NULL
                    AND "jsonData" = '{}'
                )
        ) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("check_offer_linked_to_product_constraint", table_name="offer")
