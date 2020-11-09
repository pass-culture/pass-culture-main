"""rename transaction id into payment message id

Revision ID: 99339c9d58b1
Revises: 53d63e0caa42
Create Date: 2019-05-16 08:51:00.468745

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '99339c9d58b1'
down_revision = '53d63e0caa42'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('payment', 'transactionId', new_column_name='paymentMessageId')



def downgrade():
    op.alter_column('payment', 'paymentMessageId', new_column_name='transactionId')
