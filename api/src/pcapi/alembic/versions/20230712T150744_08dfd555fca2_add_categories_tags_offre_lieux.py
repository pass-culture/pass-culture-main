"""
add categories to offer and venue tags
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "08dfd555fca2"
down_revision = "405f222670b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "criterion_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.String(length=140), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("label"),
    )
    op.create_table(
        "criterion_category_mapping",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("criterionId", sa.BigInteger(), nullable=False),
        sa.Column("categoryId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["criterion_category.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criterionId"], ["criterion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("criterionId", "categoryId", name="unique_criterion_category"),
    )
    op.create_index(
        op.f("ix_criterion_category_mapping_categoryId"),
        "criterion_category_mapping",
        ["categoryId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_criterion_category_mapping_criterionId"), "criterion_category_mapping", ["criterionId"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_criterion_category_mapping_criterionId"), table_name="criterion_category_mapping")
    op.drop_index(op.f("ix_criterion_category_mapping_categoryId"), table_name="criterion_category_mapping")
    op.drop_table("criterion_category_mapping")
    op.drop_table("criterion_category")
