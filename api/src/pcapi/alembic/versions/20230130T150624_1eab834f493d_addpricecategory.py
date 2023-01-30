"""addPriceCategory
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1eab834f493d"
down_revision = "c35e1552415c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_category_label",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("label", "venueId", name="unique_label_venue"),
    )
    op.create_index(op.f("ix_price_category_label_venueId"), "price_category_label", ["venueId"], unique=False)
    op.create_table(
        "price_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("priceCategoryLabelId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["priceCategoryLabelId"],
            ["price_category_label.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_category_offerId"), "price_category", ["offerId"], unique=False)
    op.create_index(
        op.f("ix_price_category_priceCategoryLabelId"), "price_category", ["priceCategoryLabelId"], unique=False
    )
    op.add_column("booking", sa.Column("priceCategoryLabel", sa.Text(), nullable=True))
    op.add_column("stock", sa.Column("priceCategoryId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_stock_priceCategoryId"), "stock", ["priceCategoryId"], unique=False)
    op.create_foreign_key(None, "stock", "price_category", ["priceCategoryId"], ["id"])
    op.create_check_constraint(
        constraint_name="check_price_is_not_negative",
        table_name="price_category",
        condition="price >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("check_price_is_not_negative", "price_category")
    op.drop_constraint("stock_priceCategoryId_fkey", "stock", type_="foreignkey")
    op.drop_index(op.f("ix_stock_priceCategoryId"), table_name="stock")
    op.drop_column("stock", "priceCategoryId")
    op.drop_column("booking", "priceCategoryLabel")
    op.drop_index(op.f("ix_price_category_priceCategoryLabelId"), table_name="price_category")
    op.drop_index(op.f("ix_price_category_offerId"), table_name="price_category")
    op.drop_table("price_category")
    op.drop_index(op.f("ix_price_category_label_venueId"), table_name="price_category_label")
    op.drop_table("price_category_label")
