"""Add feature table

Revision ID: d4c38884d642
Revises: ec8d3f04eba3
Create Date: 2019-03-13 15:05:49.681745

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd4c38884d642'
down_revision = 'ec8d3f04eba3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feature',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.String(300), nullable=False),
        sa.Column('isActive', sa.Boolean, nullable=False, default=False)
    )


def downgrade():
    op.drop_table('feature')
