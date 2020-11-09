"""make name nullable on user

Revision ID: 841be4ca6668
Revises: caccd0cef52f
Create Date: 2018-10-01 15:24:57.383252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '841be4ca6668'
down_revision = 'caccd0cef52f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'firstName', existing_type=sa.VARCHAR(length=35), nullable=True)
    op.alter_column('user', 'lastName', existing_type=sa.VARCHAR(length=35), nullable=True)
    pass


def downgrade():
    op.alter_column('user', 'firstName', existing_type=sa.VARCHAR(length=35), nullable=False)
    op.alter_column('user', 'lastName', existing_type=sa.VARCHAR(length=35), nullable=False)
    pass
