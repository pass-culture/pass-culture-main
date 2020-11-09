"""Add isActive to Mediation

Revision ID: 6d1eec337686
Revises: ea836848f102
Create Date: 2018-08-23 15:09:05.266174

"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression


revision = '6d1eec337686'
down_revision = 'ea836848f102'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mediation', sa.Column('isActive', sa.Boolean(), nullable=False, server_default=expression.true()))


def downgrade():
    pass
