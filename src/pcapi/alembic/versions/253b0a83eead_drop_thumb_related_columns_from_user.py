"""drop firstThumbDominantColor and thumbCount from user

Revision ID: 253b0a83eead
Revises: 565f79cfa5b2
Create Date: 2019-05-28 15:30:45.222202

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '253b0a83eead'
down_revision = '565f79cfa5b2'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('user', 'firstThumbDominantColor')
    op.drop_column('user', 'thumbCount')


def downgrade():
    op.add_column('user', sa.Column('firstThumbDominantColor', sa.LargeBinary(3), nullable=True))
    op.add_column('user', sa.Column('thumbCount', sa.INTEGER, nullable=False, server_default='0'))
