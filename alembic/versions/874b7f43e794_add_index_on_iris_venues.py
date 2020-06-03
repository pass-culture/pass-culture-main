"""add_index_on_iris_venues

Revision ID: 874b7f43e794
Revises: 9fb1d7dda237
Create Date: 2020-06-03 12:34:29.575336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '874b7f43e794'
down_revision = '9fb1d7dda237'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_iris_venues_irisId'), 'iris_venues', ['irisId'], unique=False)


def downgrade():
    op.drop_index('ix_iris_venues_irisId', table_name='iris_venues')
