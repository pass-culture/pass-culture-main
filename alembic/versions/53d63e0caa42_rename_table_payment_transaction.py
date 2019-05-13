"""Rename table PaymentTransaction into PaymentMessage

Revision ID: 53d63e0caa42
Revises: 3a9f3585d8da
Create Date: 2019-05-13 08:36:01.261394

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '53d63e0caa42'
down_revision = '3a9f3585d8da'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('payment_transaction', 'payment_message')
    op.execute('ALTER SEQUENCE payment_transaction_id_seq RENAME TO payment_message_id_seq')
    op.execute('ALTER INDEX payment_transaction_pkey RENAME TO payment_message_pkey')
    op.execute('ALTER INDEX payment_transaction_checksum_key RENAME TO payment_message_checksum_key')
    op.execute('ALTER INDEX "payment_transaction_messageId_key" RENAME TO "payment_message_messageId_key"')
    op.execute('ALTER TABLE payment RENAME CONSTRAINT "payment_transactionId_fkey" TO "payment_messageId_fkey"')


def downgrade():
    op.rename_table('payment_message', 'payment_transaction')
    op.execute('ALTER SEQUENCE payment_message_id_seq RENAME TO payment_transaction_id_seq')
    op.execute('ALTER INDEX payment_message_pkey RENAME TO payment_transaction_pkey')
    op.execute('ALTER INDEX payment_message_checksum_key RENAME TO payment_transaction_checksum_key')
    op.execute('ALTER INDEX "payment_message_messageId_key" RENAME TO "payment_transaction_messageId_key"')
    op.execute('ALTER TABLE payment RENAME CONSTRAINT "payment_messageId_fkey" TO "payment_transactionId_fkey"')
