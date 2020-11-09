"""add_public_name_to_venue

Revision ID: c3fb24563ff0
Revises: ddf0dc458d57
Create Date: 2019-04-19 08:04:15.895020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3fb24563ff0'
down_revision = 'd76f83432485'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('venue', sa.Column('publicName', sa.VARCHAR(255), nullable=True))


def downgrade():
    op.drop_column('venue', 'publicName')
