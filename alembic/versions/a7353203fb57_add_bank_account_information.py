"""add IBAN and BIC to offerer

Revision ID: a7353203fb57
Revises: 5f072f461580
Create Date: 2018-09-19 13:54:44.493421

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a7353203fb57'
down_revision = '5f072f461580'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('offerer', sa.Column('IBAN', sa.VARCHAR(27), nullable=True))
    op.add_column('offerer', sa.Column('BIC', sa.VARCHAR(11), nullable=True))
    op.create_check_constraint(constraint_name='check_IBAN_and_BIC_xor_not_IBAN_and_not_BIC',
                               table_name='offerer',
                               condition='("IBAN" IS NULL AND "BIC" IS NULL) OR ("IBAN" IS NOT NULL AND "BIC" IS NOT NULL)'
                               )


def downgrade():
    op.drop_column('offerer', 'IBAN')
    op.drop_column('offerer', 'BIC')
