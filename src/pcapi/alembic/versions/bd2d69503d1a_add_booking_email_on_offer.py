"""Add bookingEmail column on table offer

Revision ID: bd2d69503d1a
Revises: 6d1eec337686
Create Date: 2018-08-28 11:47:37.489626

"""
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = 'bd2d69503d1a'
down_revision = '2268bcb671a5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('offer', sa.Column('bookingEmail', sa.VARCHAR(120), nullable=True, server_default=expression.null()))


def downgrade():
    pass
