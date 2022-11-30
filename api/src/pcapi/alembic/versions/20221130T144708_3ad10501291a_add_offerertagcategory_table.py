"""Add_OffererTagCategory_table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3ad10501291a"
down_revision = "dfea3ac0b326"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_offerer_tag_categoryId", table_name="offerer_tag")
    op.drop_column("offerer_tag", "categoryId")

    op.create_table(
        "offerer_tag_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("label", sa.String(length=140), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "offerer_tag_category_mapping",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tagId", sa.BigInteger(), nullable=False),
        sa.Column("categoryId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["offerer_tag_category.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tagId"], ["offerer_tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tagId", "categoryId", name="unique_offerer_tag_category"),
    )
    op.create_index(
        op.f("ix_offerer_tag_category_mapping_categoryId"), "offerer_tag_category_mapping", ["categoryId"], unique=False
    )
    op.create_index(
        op.f("ix_offerer_tag_category_mapping_tagId"), "offerer_tag_category_mapping", ["tagId"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_offerer_tag_category_mapping_tagId"), table_name="offerer_tag_category_mapping")
    op.drop_index(op.f("ix_offerer_tag_category_mapping_categoryId"), table_name="offerer_tag_category_mapping")
    op.drop_table("offerer_tag_category_mapping")
    op.drop_table("offerer_tag_category")

    op.add_column("offerer_tag", sa.Column("categoryId", sa.TEXT(), autoincrement=False, nullable=True))
    op.create_index("ix_offerer_tag_categoryId", "offerer_tag", ["categoryId"], unique=False)
