"""
Add UserTag, UserTagCategory, UserTagCategoryMapping and UserTagMapping tables,
they are used to manage tags applied on beneficiaries
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0c061fe70acc"
down_revision = "fa3f1609ac73"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_tag",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user_tag_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user_tag_category_mapping",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tagId", sa.BigInteger(), nullable=False),
        sa.Column("categoryId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["categoryId"], ["user_tag_category.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tagId"], ["user_tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tagId", "categoryId", name="unique_user_tag_category"),
    )
    op.create_index(
        op.f("ix_user_tag_category_mapping_categoryId"),
        "user_tag_category_mapping",
        ["categoryId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_tag_category_mapping_tagId"),
        "user_tag_category_mapping",
        ["tagId"],
        unique=False,
    )
    op.create_table(
        "user_tag_mapping",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("tagId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["tagId"], ["user_tag.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "tagId", name="unique_user_tag"),
    )
    op.create_index(op.f("ix_user_tag_mapping_tagId"), "user_tag_mapping", ["tagId"], unique=False)
    op.create_index(op.f("ix_user_tag_mapping_userId"), "user_tag_mapping", ["userId"], unique=False)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_table("user_tag_mapping", if_exists=True)
        op.drop_table("user_tag_category_mapping", if_exists=True)
        op.drop_table("user_tag_category", if_exists=True)
        op.drop_table("user_tag", if_exists=True)
