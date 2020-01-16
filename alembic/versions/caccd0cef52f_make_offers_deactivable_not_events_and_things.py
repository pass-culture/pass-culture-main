"""make offers deactivable, not events and things

Revision ID: caccd0cef52f
Revises: a7353203fb57
Create Date: 2018-09-20 11:20:37.272195

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = 'caccd0cef52f'
down_revision = 'a7353203fb57'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('offer', sa.Column('isActive', sa.Boolean(), nullable=False, server_default=expression.true()))
    op.drop_column('event', 'isActive')
    op.drop_column('thing', 'isActive')


def downgrade():
    op.add_column('event', sa.Column('isActive', sa.Boolean(), nullable=False, server_default=expression.true()))
    op.add_column('thing', sa.Column('isActive', sa.Boolean(), nullable=False, server_default=expression.true()))
    op.drop_column('offer', 'isActive')
