"""add_provider_enabled_for_pro

Revision ID: 035f0ee8ea70
Revises: e945f921cc69
Create Date: 2019-06-25 12:12:52.207776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = '035f0ee8ea70'
down_revision = 'e945f921cc69'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('provider', sa.Column('enabledForPro', sa.Boolean(), nullable=False, server_default=expression.false()))


def downgrade():
    op.drop_column('provider', 'enabledForPro')
