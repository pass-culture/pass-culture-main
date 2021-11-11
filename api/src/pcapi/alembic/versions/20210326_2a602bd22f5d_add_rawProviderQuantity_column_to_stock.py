"""add_rawProviderQuantity_column_to_stock

Revision ID: 2a602bd22f5d
Revises: 4a0337b7cbbc
Create Date: 2021-03-26 16:19:31.170453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a602bd22f5d"
down_revision = "4a0337b7cbbc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("stock", sa.Column("rawProviderQuantity", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("stock", "rawProviderQuantity")
