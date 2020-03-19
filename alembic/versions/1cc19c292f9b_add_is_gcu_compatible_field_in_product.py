"""add_is_gcu_compatible_field_in_product

Revision ID: 1cc19c292f9b
Revises: 1f446f8a334d
Create Date: 2020-03-19 11:01:46.909306

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = '1cc19c292f9b'
down_revision = '1f446f8a334d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product', sa.Column('isGcuCompatible', sa.Boolean, nullable=False, server_default=expression.true()))


def downgrade():
    op.drop_column('product', 'isGcuCompatible')
