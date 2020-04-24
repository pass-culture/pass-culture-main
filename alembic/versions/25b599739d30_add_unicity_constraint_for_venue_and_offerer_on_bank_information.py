"""add_unicity_constraint_for_venue_and_offerer_on_bank_information

Revision ID: 25b599739d30
Revises: 040875ff5d5b
Create Date: 2020-04-21 12:15:20.622510

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25b599739d30'
down_revision = '040875ff5d5b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('idx_bank_information_offererId', table_name='bank_information')
    op.drop_index('idx_bank_information_venueId', table_name='bank_information')
    op.create_index(op.f('idx_bank_information_offererId'), 'bank_information', ['offererId'], unique=True)
    op.create_index(op.f('idx_bank_information_venueId'), 'bank_information', ['venueId'], unique=True)


def downgrade():
    op.drop_index('idx_bank_information_offererId', table_name='bank_information')
    op.drop_index('idx_bank_information_venueId', table_name='bank_information')
    op.create_index(op.f('idx_bank_information_offererId'), 'bank_information', ['offererId'], unique=False)
    op.create_index(op.f('idx_bank_information_venueId'), 'bank_information', ['venueId'], unique=False)
