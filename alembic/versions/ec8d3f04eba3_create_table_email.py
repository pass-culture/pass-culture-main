"""create email_failed table

Revision ID: ec8d3f04eba3
Revises: fdcdc5e96f15
Create Date: 2019-03-05 10:32:57.212731

"""
import sqlalchemy as sa
from alembic import op
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'ec8d3f04eba3'
down_revision = 'fdcdc5e96f15'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'email',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('content', sa.JSON, nullable=False),
        sa.Column('status', sa.String(12), nullable=False),
        sa.Column('datetime', sa.DateTime, nullable=True, default=datetime.utcnow),
    )


def downgrade():
    op.drop_table('email')
