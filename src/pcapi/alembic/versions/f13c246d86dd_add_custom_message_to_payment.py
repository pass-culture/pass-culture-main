"""Add custom message column to table Payment

Revision ID: f13c246d86dd
Revises: 573342f77706
Create Date: 2018-12-21 12:59:25.613016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f13c246d86dd'
down_revision = '573342f77706'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('payment', sa.Column('customMessage', sa.VARCHAR(140), nullable=True))


def downgrade():
    op.drop_column('payment', 'customMessage')
