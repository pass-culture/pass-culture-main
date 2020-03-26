"""add_default_value_for_isGcuCompatible_in_product

Revision ID: a3be5be5ad3d
Revises: 48440c1d122a
Create Date: 2020-03-19 15:36:33.558492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = 'a3be5be5ad3d'
down_revision = '48440c1d122a'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('product', 'isGcuCompatible', server_default=expression.true(), nullable=False)


def downgrade():
    op.alter_column('product', 'isGcuCompatible', nullable=True)
