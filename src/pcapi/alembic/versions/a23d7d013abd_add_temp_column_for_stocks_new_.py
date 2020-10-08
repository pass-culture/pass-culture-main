"""add_temp_column_for_stocks_new_constraint

Revision ID: a23d7d013abd
Revises: 387d27fbe92d
Create Date: 2020-03-26 13:39:46.842574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a23d7d013abd'
down_revision = '387d27fbe92d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock', sa.Column('hasBeenMigrated', sa.BOOLEAN, nullable=True))


def downgrade():
    op.drop_column('stock', 'hasBeenMigrated')

