"""Drop column user.hasSeenTutorials

Revision ID: 0511102bcb21
Revises: 52b7d4d03980

"""
from alembic import op
import sqlalchemy as sa


revision = "0511102bcb21"
down_revision = "52b7d4d03980"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "hasSeenTutorials")


def downgrade():
    op.add_column("user", sa.Column("hasSeenTutorials", sa.Boolean(), nullable=True))
