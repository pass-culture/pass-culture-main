"""empty message

Revision ID: da60df7693ba
Revises: 9f958c5e2435
Create Date: 2018-08-23 12:20:01.149618

"""
from alembic import op
from models import Booking


# revision identifiers, used by Alembic.
revision = 'da60df7693ba'
down_revision = '9f958c5e2435'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
      'BEGIN TRANSACTION;'
        'ALTER TABLE "booking" ADD COLUMN "isCancelled" BOOLEAN DEFAULT False;'
        + Booking.trig_ddl + ';'
      'COMMIT;')
    pass


def downgrade():
    pass
