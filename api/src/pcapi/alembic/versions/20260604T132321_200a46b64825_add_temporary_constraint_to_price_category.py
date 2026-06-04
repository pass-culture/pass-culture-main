"""Add constraint on price_category: check_has_label_or_price_category_label (1/2)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "200a46b64825"
down_revision = "655d2fa1f6b1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "price_category" DROP CONSTRAINT IF EXISTS "check_has_label_or_price_category_label";
        ALTER TABLE "price_category" ADD CONSTRAINT "check_has_label_or_price_category_label" CHECK ((label IS NOT NULL) OR ("priceCategoryLabelId" IS NOT NULL)) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("check_has_label_or_price_category_label", table_name="price_category")
