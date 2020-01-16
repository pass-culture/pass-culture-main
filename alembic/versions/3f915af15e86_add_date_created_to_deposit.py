"""add dateCreated to deposit

Revision ID: 3f915af15e86
Revises: 67086f4e9aa5
Create Date: 2019-01-24 16:01:37.830576

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3f915af15e86'
down_revision = '67086f4e9aa5'
branch_labels = None
depends_on = None



def upgrade():
    op.add_column('deposit', sa.Column('dateCreated', sa.DateTime(), nullable=False, server_default='1900-01-01 00:00:00'))


def downgrade():
    op.drop_column('deposit', 'dateCreated')