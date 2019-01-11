"""Rename PaymentTransaction hash to checksum

Revision ID: e04099025fe9
Revises: 67086f4e9aa5
Create Date: 2019-01-11 16:18:43.945969

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e04099025fe9'
down_revision = 'b73fa4d77710'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('payment_transaction', 'hash', new_column_name='checksum')


def downgrade():
    op.alter_column('payment_transaction', 'checksum', new_column_name='hash')
