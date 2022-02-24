"""Create offerer_tag table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ca95cbf376a1"
down_revision = "e289b8d9cbe9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "offerer_tag",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "offerer_tag_mapping",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=False),
        sa.Column("tagId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tagId"], ["offerer_tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("offererId", "tagId", name="unique_offerer_tag"),
    )
    op.create_index(op.f("ix_offerer_tag_mapping_offererId"), "offerer_tag_mapping", ["offererId"], unique=False)
    op.create_index(op.f("ix_offerer_tag_mapping_tagId"), "offerer_tag_mapping", ["tagId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_offerer_tag_mapping_tagId"), table_name="offerer_tag_mapping")
    op.drop_index(op.f("ix_offerer_tag_mapping_offererId"), table_name="offerer_tag_mapping")
    op.drop_table("offerer_tag_mapping")
    op.drop_table("offerer_tag")
