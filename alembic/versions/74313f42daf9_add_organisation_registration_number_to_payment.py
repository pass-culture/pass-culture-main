"""Add organisation registration number to payment

Revision ID: 74313f42daf9
Revises: 9f55a2d1a269
Create Date: 2018-11-20 16:21:15.383241

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '74313f42daf9'
down_revision = '9f55a2d1a269'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('payment', sa.Column('organisationRegistrationNumber', sa.VARCHAR(14), nullable=False))


def downgrade():
    op.drop_column('payment', 'organisationRegistrationNumber')
