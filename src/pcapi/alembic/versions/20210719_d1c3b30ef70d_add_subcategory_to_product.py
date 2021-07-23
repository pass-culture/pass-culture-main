"""add_subcategory_to_product

Revision ID: d1c3b30ef70d
Revises: ffce4944b6b7
Create Date: 2021-07-19 14:28:35.887679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d1c3b30ef70d"
down_revision = "ffce4944b6b7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("product", sa.Column("subcategoryId", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("product", "subcategoryId")
