"""add isDuo to offer

Revision ID: eda764ae6b37
Revises: 914fef4f49ab
Create Date: 2019-10-11 08:57:18.433458

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = 'eda764ae6b37'
down_revision = '914fef4f49ab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('offer', sa.Column('isDuo', sa.Boolean, nullable=False, server_default=expression.false()))


def downgrade():
    op.drop_column('offer', 'isDuo')
