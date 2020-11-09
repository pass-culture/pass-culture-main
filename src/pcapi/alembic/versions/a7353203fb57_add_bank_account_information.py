"""add IBAN and BIC to offerer

Revision ID: a7353203fb57
Revises: 5f072f461580
Create Date: 2018-09-19 13:54:44.493421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7353203fb57'
down_revision = '271d090148dc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('offerer', sa.Column('iban', sa.VARCHAR(27), nullable=True))
    op.add_column('offerer', sa.Column('bic', sa.VARCHAR(11), nullable=True))
    op.create_check_constraint(constraint_name='check_iban_and_bic_xor_not_iban_and_not_bic',
                               table_name='offerer',
                               condition='("iban" IS NULL AND "bic" IS NULL) OR ("iban" IS NOT NULL AND "bic" IS NOT NULL)'
                               )


def downgrade():
    op.drop_column('offerer', 'iban')
    op.drop_column('offerer', 'bic')
