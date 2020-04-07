"""add_index_on_product_isCguCompatible

Revision ID: 1017c2c5a6f8
Revises: a23d7d013abd
Create Date: 2020-04-07 15:03:42.305039

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '1017c2c5a6f8'
down_revision = 'a23d7d013abd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute('CREATE INDEX CONCURRENTLY product_isGcuCompatible ON product ("isGcuCompatible");')


def downgrade():
    op.execute('DROP INDEX IF EXISTS product_isGcuCompatible;')
