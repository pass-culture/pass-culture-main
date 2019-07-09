"""add_favorite_feature

Revision ID: 37ba62c7fdb3
Revises: 926f236ee66f
Create Date: 2019-07-09 09:47:32.341098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = '37ba62c7fdb3'
down_revision = '926f236ee66f'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('recommendation', 'isFavorite')


def downgrade():
    op.add_column('recommendation', sa.Column('isFavorite', sa.Boolean, nullable=False, server_default=expression.false()))
