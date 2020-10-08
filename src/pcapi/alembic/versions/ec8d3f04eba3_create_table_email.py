"""create email table

Revision ID: ec8d3f04eba3
Revises: fdcdc5e96f15
Create Date: 2019-03-05 10:32:57.212731

"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
from pcapi.models.email import EmailStatus

revision = 'ec8d3f04eba3'
down_revision = 'fdcdc5e96f15'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'email',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('content', sa.JSON, nullable=False),
        sa.Column('status', sa.Enum(EmailStatus), nullable=False),
        sa.Column('datetime', sa.DateTime, nullable=True, default=datetime.utcnow),
    )
    op.create_index(op.f('ix_status'), 'email', ['status'], unique=False)


def downgrade():
    op.drop_table('email')
