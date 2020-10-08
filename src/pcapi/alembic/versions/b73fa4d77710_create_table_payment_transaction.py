"""Create table PaymentTransaction

Revision ID: b73fa4d77710
Revises: f13c246d86dd
Create Date: 2018-12-27 09:47:46.706893

"""
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey

from pcapi.models.payment_status import TransactionStatus

revision = 'b73fa4d77710'
down_revision = 'f13c246d86dd'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('payment', 'transactionMessageId')
    op.alter_column('payment_status', 'status', existing_type=sa.Enum(TransactionStatus), nullable=False)
    op.create_table(
        'payment_transaction',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('messageId', sa.String(50), unique=True, nullable=False),
        sa.Column('checksum', sa.String(40), unique=True, nullable=False)
    )
    op.add_column(
        'payment',
        sa.Column('transactionId', sa.BigInteger, ForeignKey('payment_transaction.id'), nullable=True)
    )


def downgrade():
    op.add_column('payment', sa.Column('transactionMessageId', sa.VARCHAR(50), nullable=True))
    op.drop_column('payment', 'transactionId')
    op.drop_table('payment_transaction')
