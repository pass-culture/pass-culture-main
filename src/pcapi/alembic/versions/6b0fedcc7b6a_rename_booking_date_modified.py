"""Rename column Booking.dateModified to dateCreated

Revision ID: 6b0fedcc7b6a
Revises: 3bc420f1160a
Create Date: 2018-10-16 09:07:20.508703

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '6b0fedcc7b6a'
down_revision = '4e18b6798915'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('booking', 'dateModified', new_column_name='dateCreated')


def downgrade():
    op.alter_column('booking', 'dateCreated', new_column_name='dateModified')
