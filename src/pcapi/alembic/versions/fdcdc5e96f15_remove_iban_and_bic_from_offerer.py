"""remove bic and iban from offerer and venue

Revision ID: fdcdc5e96f15
Revises: 4462a541eeed
Create Date: 2019-02-25 14:00:09.426202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdcdc5e96f15'
down_revision = '4462a541eeed'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('offerer', 'iban')
    op.drop_column('offerer', 'bic')
    op.drop_column('venue', 'iban')
    op.drop_column('venue', 'bic')


def downgrade():
    op.add_column('offerer', sa.Column('iban', sa.VARCHAR(27), nullable=True))
    op.add_column('offerer', sa.Column('bic', sa.VARCHAR(11), nullable=True))
    op.create_check_constraint(constraint_name='check_iban_and_bic_xor_not_iban_and_not_bic',
                               table_name='offerer',
                               condition='("iban" IS NULL AND "bic" IS NULL) OR ("iban" IS NOT NULL AND "bic" IS NOT NULL)'
                               )
    op.add_column('venue', sa.Column('iban', sa.VARCHAR(27), nullable=True))
    op.add_column('venue', sa.Column('bic', sa.VARCHAR(11), nullable=True))
    op.create_check_constraint(constraint_name='check_iban_and_bic_xor_not_iban_and_not_bic',
                               table_name='venue',
                               condition='("iban" IS NULL AND "bic" IS NULL) OR ("iban" IS NOT NULL AND "bic" IS NOT NULL)'
                               )
