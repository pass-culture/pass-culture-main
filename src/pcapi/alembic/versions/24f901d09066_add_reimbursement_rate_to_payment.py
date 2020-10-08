"""Add column reimbursementRate to Payment

Revision ID: 24f901d09066
Revises: 500ce8194cff
Create Date: 2018-12-17 12:25:47.173374

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '24f901d09066'
down_revision = '500ce8194cff'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('payment', sa.Column('reimbursementRate', sa.Numeric(10, 2), nullable=False))


def downgrade():
    op.drop_column('payment', 'reimbursementRate')
