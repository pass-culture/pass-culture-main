"""Add reset password token and validity limit to user

Revision ID: ad309156b749
Revises: 10ea71b5a60b
Create Date: 2018-09-05 12:38:39.577894

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ad309156b749'
down_revision = '8be876a5e4c3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('resetPasswordToken', sa.VARCHAR(10), unique=True, nullable=True))
    op.add_column('user', sa.Column('resetPasswordTokenValidityLimit', sa.DateTime, nullable=True))


def downgrade():
    pass
