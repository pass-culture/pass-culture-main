"""create_allocine_pivot_table

Revision ID: 8f2c1fd24cad
Revises: ed5ca9bde4a9
Create Date: 2020-01-07 09:17:24.303580

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '8f2c1fd24cad'
down_revision = 'ed5ca9bde4a9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'allocine_pivot',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('siret', sa.VARCHAR(14), nullable=False, unique=True),
        sa.Column('theaterId', sa.VARCHAR(20), nullable=False, unique=True)
    )


def downgrade():
    op.drop_table('allocine_pivot')
