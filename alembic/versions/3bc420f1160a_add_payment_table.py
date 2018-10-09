"""Add payment table

Revision ID: 3bc420f1160a
Revises: 700126ecaf1d
Create Date: 2018-10-09 14:27:52.050628

"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey, func

from models.payment import PaymentStatus

revision = '3bc420f1160a'
down_revision = '700126ecaf1d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'payment',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('dateCreated', sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column('bookingId', sa.BigInteger, ForeignKey("booking.id"), index=True, nullable=False),
        sa.Column('offererId', sa.BigInteger, ForeignKey("offerer.id"), index=True, nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('type', sa.VARCHAR, nullable=False),
        sa.Column('iban', sa.VARCHAR(27), nullable=True),
        sa.Column('status', sa.Enum(PaymentStatus), nullable=False, server_default=PaymentStatus.PENDING),
        sa.Column('dateStatus', sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('author', sa.VARCHAR(27), nullable=False)
    )


def downgrade():
    op.drop_table('payment')
