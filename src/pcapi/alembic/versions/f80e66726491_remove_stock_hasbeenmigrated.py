"""remove_stock_hasbeenmigrated

Revision ID: f80e66726491
Revises: 0c6a4a8bbcdb
Create Date: 2020-11-06 16:39:31.088755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f80e66726491'
down_revision = '0c6a4a8bbcdb'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('stock', 'hasBeenMigrated')


def downgrade():
    op.add_column('stock', sa.Column('hasBeenMigrated', sa.BOOLEAN, nullable=True))
