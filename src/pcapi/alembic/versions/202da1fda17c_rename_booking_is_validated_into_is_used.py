"""change isValidated into isUsed in booking model

Revision ID: 202da1fda17c
Revises: ad309156b749
Create Date: 2018-09-10 08:51:06.005170

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '202da1fda17c'
down_revision = '43a686a11027'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('booking', 'isValidated', new_column_name='isUsed')


def downgrade():
    op.alter_column('booking', 'isUsed', new_column_name='isValidated')
