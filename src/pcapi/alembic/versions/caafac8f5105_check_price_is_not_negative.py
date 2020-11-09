"""Stock.price cannot be negative

Revision ID: caafac8f5105
Revises: 6b0fedcc7b6a
Create Date: 2018-10-17 15:15:22.921880

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'caafac8f5105'
down_revision = '6b0fedcc7b6a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        constraint_name='check_price_is_not_negative',
        table_name='stock',
        condition='price >= 0'
    )


def downgrade():
    op.drop_constraint('check_price_is_not_negative', 'stock')
