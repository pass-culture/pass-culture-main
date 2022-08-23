"""add_label_and_description_into_offerer_tag_table
"""
from alembic import op
import sqlalchemy as sa


revision = "0502f0f2f72c"
down_revision = "4df590d6ffb3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offerer_tag", sa.Column("label", sa.String(length=140), nullable=True))
    op.add_column("offerer_tag", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("offerer_tag", "description")
    op.drop_column("offerer_tag", "label")
