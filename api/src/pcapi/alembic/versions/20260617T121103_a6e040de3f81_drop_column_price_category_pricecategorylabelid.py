"""Drop column: price_category.priceCategoryLabelId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a6e040de3f81"
down_revision = "7e63b963a447"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("price_category", "priceCategoryLabelId")


def downgrade() -> None:
    op.add_column("price_category", sa.Column("priceCategoryLabelId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_foreign_key(
        op.f("price_category_priceCategoryLabelId_fkey"),
        "price_category",
        "price_category_label",
        ["priceCategoryLabelId"],
        ["id"],
    )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_price_category_priceCategoryLabelId"),
            "price_category",
            ["priceCategoryLabelId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
