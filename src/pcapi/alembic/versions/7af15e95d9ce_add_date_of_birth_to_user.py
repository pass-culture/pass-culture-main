"""Add date of birth to user

Revision ID: 7af15e95d9ce
Revises: 9f55a2d1a269
Create Date: 2018-11-19 14:59:14.673256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7af15e95d9ce"
down_revision = "9f55a2d1a269"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("dateOfBirth", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("user", "dateOfBirth")
