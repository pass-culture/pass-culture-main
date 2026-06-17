"""Add NOT NULL constraint on "price_category.label" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7e63b963a447"
down_revision = "ec0b3454ed61"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("price_category_label_not_null_constraint", table_name="price_category")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "price_category" ADD CONSTRAINT "price_category_label_not_null_constraint" CHECK ("label" IS NOT NULL) NOT VALID"""
    )
