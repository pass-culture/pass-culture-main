"""Modify payment status enum values

Revision ID: f9361bb484a1
Revises: c3fb24563ff0
Create Date: 2019-05-03 13:27:47.709905

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f9361bb484a1'
down_revision = '243db387e3c2'
branch_labels = None
depends_on = None

previous_values = ('PENDING', 'NOT_PROCESSABLE', 'SENT', 'ERROR', 'SUCCESS')
new_values = ('PENDING', 'NOT_PROCESSABLE', 'SENT', 'ERROR', 'RETRY')

previous_enum = sa.Enum(*previous_values, name='transactionstatus')
new_enum = sa.Enum(*new_values, name='transactionstatus')
temporary_enum = sa.Enum(*new_values, name='tmp_transactionstatus')


def upgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE payment_status ALTER COLUMN status TYPE tmp_transactionstatus'
               ' USING status::text::tmp_transactionstatus')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE payment_status ALTER COLUMN status TYPE transactionstatus'
               ' USING status::text::transactionstatus')
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE payment_status ALTER COLUMN status TYPE tmp_transactionstatus'
               ' USING status::text::tmp_transactionstatus')
    new_enum.drop(op.get_bind(), checkfirst=False)
    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE payment_status ALTER COLUMN status TYPE transactionstatus'
               ' USING status::text::transactionstatus')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
