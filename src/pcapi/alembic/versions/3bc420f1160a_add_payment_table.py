'''Add payment and payment status table

Revision ID: 3bc420f1160a
Revises: 700126ecaf1d
Create Date: 2018-10-09 14:27:52.050628

'''

from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey
from sqlalchemy import func

from pcapi.models.payment_status import TransactionStatus


revision = '3bc420f1160a'
down_revision = '700126ecaf1d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'payment',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('author', sa.VARCHAR(27), nullable=False),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('recipient', sa.VARCHAR(140), nullable=True),
        sa.Column('iban', sa.VARCHAR(27), nullable=True),
        sa.Column('bic', sa.VARCHAR(11), nullable=True),
        sa.Column('bookingId', sa.BigInteger, ForeignKey('booking.id'), index=True, nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('reimbursementRule', sa.VARCHAR(200), nullable=False),
        sa.Column('paymentTransactionId', sa.VARCHAR(50), nullable=True)
    )

    op.create_table(
        'payment_status',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('paymentId', sa.BigInteger, ForeignKey('payment.id'), nullable=False),
        sa.Column('date', sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column('status', sa.Enum(TransactionStatus), nullable=False),
        sa.Column('detail', sa.VARCHAR, nullable=True)
    )


def downgrade():
    op.drop_table('payment_status')
    op.execute('drop type transactionstatus;')
    op.drop_table('payment')
