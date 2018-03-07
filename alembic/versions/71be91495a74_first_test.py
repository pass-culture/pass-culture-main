"""first test

Revision ID: 71be91495a74
Revises:
Create Date: 2018-02-14 15:53:51.669009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71be91495a74'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(200)),
    )

def downgrade():
    op.drop_table('account')
