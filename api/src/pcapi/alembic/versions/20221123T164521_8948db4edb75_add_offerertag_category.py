"""Add_OffererTag_category
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8948db4edb75"
down_revision = "8b0574f4aa1b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offerer_tag", sa.Column("categoryId", sa.Text(), nullable=True))
    op.create_index(op.f("ix_offerer_tag_categoryId"), "offerer_tag", ["categoryId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_offerer_tag_categoryId"), table_name="offerer_tag")
    op.drop_column("offerer_tag", "categoryId")
