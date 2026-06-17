"""Add NOT NULL constraint on "price_category.label" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "961aa73aca15"
down_revision = "30b503841791"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "price_category" DROP CONSTRAINT IF EXISTS "price_category_label_not_null_constraint";
        ALTER TABLE "price_category" ADD CONSTRAINT "price_category_label_not_null_constraint" CHECK ("label" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("price_category_label_not_null_constraint", table_name="price_category")
