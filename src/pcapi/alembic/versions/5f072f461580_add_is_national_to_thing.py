"""Add isNational to thing

Revision ID: 5f072f461580
Revises: 202da1fda17c
Create Date: 2018-09-17 12:36:46.498574

"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression


revision = '5f072f461580'
down_revision = '202da1fda17c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('thing', sa.Column('isNational', sa.Boolean(), nullable=False, server_default=expression.false()))


def downgrade():
    op.drop_column('thing', 'isNational')
