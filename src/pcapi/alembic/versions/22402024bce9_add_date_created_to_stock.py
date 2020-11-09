"""add_date_created_to_stock

Revision ID: 22402024bce9
Revises: 0fc312879579
Create Date: 2019-12-04 14:39:39.265712

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22402024bce9'
down_revision = '0fc312879579'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock', sa.Column('dateCreated', sa.DateTime, nullable=True, server_default='1900-01-01 00:00:00'))


def downgrade():
    op.drop_column('stock', 'dateCreated')
