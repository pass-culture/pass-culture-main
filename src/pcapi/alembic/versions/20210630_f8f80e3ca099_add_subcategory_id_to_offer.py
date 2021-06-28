"""add_subcategoryId_to_offer

Revision ID: f8f80e3ca099
Revises: b59aa6de9662
Create Date: 2021-06-30 14:38:34.701860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f8f80e3ca099"
down_revision = "b59aa6de9662"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("subcategoryId", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("offer", "subcategoryId")
