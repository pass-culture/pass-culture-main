"""remove_unused_filled

Revision ID: 48440c1d122a
Revises: eb60e72463f1
Create Date: 2020-03-13 10:35:58.958527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48440c1d122a'
down_revision = 'eb60e72463f1'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('stock', 'groupSize')
    op.drop_column('stock', 'bookingRecapSent')


def downgrade():
    op.add_column('stock', sa.Column('bookingRecapSent', sa.DateTime, nullable=True))
    op.add_column('stock', sa.Column('groupSize', sa.Integer, nullable=False, server_default=1))
