"""add firstName, lastName, postalCode and phoneNumber to user

Revision ID: 271d090148dc
Revises: 5f072f461580
Create Date: 2018-09-19 12:17:44.873776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '271d090148dc'
down_revision = '5c79b8845ffe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('firstName', sa.VARCHAR(35), nullable=False, server_default=''))
    op.add_column('user', sa.Column('lastName', sa.VARCHAR(35), nullable=False, server_default=''))
    op.add_column('user', sa.Column('postalCode', sa.VARCHAR(5), nullable=False, server_default=''))
    op.add_column('user', sa.Column('phoneNumber', sa.VARCHAR(20), nullable=True))


def downgrade():
    op.drop_column('user', 'firstName')
    op.drop_column('user', 'lastName')
    op.drop_column('user', 'postalCode')
    op.drop_column('user', 'phoneNumber')
