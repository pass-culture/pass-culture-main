"""replace function wallet_balance

Revision ID: 6d93c35d097b
Revises: 72f3629849f0
Create Date: 2018-08-10 16:07:28.782900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from models import Booking

revision = '6d93c35d097b'
down_revision = '72f3629849f0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(Booking.trig_ddl)


def downgrade():
    pass
