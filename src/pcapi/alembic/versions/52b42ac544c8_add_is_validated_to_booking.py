"""add isValidated column to booking

Revision ID: 52b42ac544c8
Revises: a462a0208015
Create Date: 2018-09-05 14:35:02.335559

"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression


revision = '52b42ac544c8'
down_revision = 'a462a0208015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('booking', sa.Column('isValidated', sa.BOOLEAN, nullable=False, server_default=expression.false()))


def downgrade():
    op.drop_column('booking', 'isValidated')
