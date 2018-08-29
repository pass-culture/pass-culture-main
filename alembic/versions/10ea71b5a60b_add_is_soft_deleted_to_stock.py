"""Add isSoftDeleted Boolean to stock

Revision ID: 10ea71b5a60b
Revises: 6d1eec337686
Create Date: 2018-08-29 14:58:01.210338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = '10ea71b5a60b'
down_revision = '6d1eec337686'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock', sa.Column('isSoftDeleted', sa.BOOLEAN, nullable=False, server_default=expression.false()))


def downgrade():
    pass
