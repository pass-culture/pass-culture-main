"""delete_tutoIndex_column_mediation_table

Revision ID: 2556f5577098
Revises: 040875ff5d5b
Create Date: 2020-04-21 09:18:38.064455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2556f5577098'
down_revision = '040875ff5d5b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('mediation', 'tutoIndex')

def downgrade():
    op.add_column('mediation', sa.Column('tutoIndex', sa.Integer(), nullable=True, index=True))

