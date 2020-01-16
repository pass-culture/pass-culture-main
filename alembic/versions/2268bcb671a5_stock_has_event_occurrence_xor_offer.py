"""Stock has eventOccurrence XOR offer instead of OR

Revision ID: 2268bcb671a5
Revises: 6d1eec337686
Create Date: 2018-08-27 14:47:22.761230

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2268bcb671a5'
down_revision = 'da60df7693ba'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('check_stock_has_event_occurrence_or_offer', 'stock')
    op.create_check_constraint(constraint_name='check_stock_has_event_occurrence_xor_offer',
                               table_name='stock',
                               condition='("eventOccurrenceId" IS NOT NULL AND "offerId" IS NULL)' +
                               'OR ("eventOccurrenceId" IS NULL AND "offerId" IS NOT NULL)'
                               )


def downgrade():
    pass
