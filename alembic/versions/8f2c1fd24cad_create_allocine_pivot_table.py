"""create_allocine_pivot_table

Revision ID: 8f2c1fd24cad
Revises: 2cb37da9609e
Create Date: 2020-01-07 09:17:24.303580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey

revision = '8f2c1fd24cad'
down_revision = '2cb37da9609e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'allocine_pivot',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('venueSiret', sa.VARCHAR(14), ForeignKey('venue.siret'), nullable=False, unique=True),
        sa.Column('theaterId', sa.VARCHAR(25), nullable=False, unique=True)
    )


def downgrade():
    op.drop_table('allocine_pivot')
