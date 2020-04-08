"""add_default_value_for_isGcuCompatible_in_product

Revision ID: a3be5be5ad3d
Revises: a23d7d013abd
Create Date: 2020-03-19 15:36:33.558492

"""
from alembic import op
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = 'a3be5be5ad3d'
down_revision = 'a23d7d013abd'
branch_labels = None
depends_on = None


def upgrade():
    # op.alter_column('product', 'isGcuCompatible', nullable=False)
    op.execute('ALTER TABLE product ADD CONSTRAINT check_isCGUCompatible_is_not_null CHECK ("isGcuCompatible" IS NOT NULL) NOT VALID')
    op.alter_column('product', 'isGcuCompatible', server_default=expression.true())


def downgrade():
    op.alter_column('product', 'isGcuCompatible', server_default=None, nullable=True)
