"""Drop constraint: check_has_label_or_price_category_label"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "30b503841791"
down_revision = "042ffc4e412b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("check_has_label_or_price_category_label", table_name="price_category")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        """
        ALTER TABLE "price_category" ADD CONSTRAINT "check_has_label_or_price_category_label" CHECK ((label IS NOT NULL) OR ("priceCategoryLabelId" IS NOT NULL));
        """
    )
