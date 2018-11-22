"""Add recipient SIREN to Payment

Revision ID: 74313f42daf9
Revises: 9f55a2d1a269
Create Date: 2018-11-20 16:21:15.383241

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '74313f42daf9'
down_revision = '7af15e95d9ce'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('payment', sa.Column('recipientSiren', sa.VARCHAR(9), nullable=False))
    op.alter_column('payment', 'recipient', new_column_name='recipientName')


def downgrade():
    op.alter_column('payment', 'recipientName', new_column_name='recipient')
    op.drop_column('payment', 'recipientSiren')
