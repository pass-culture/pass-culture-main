"""add_column_hasSeenTutorials_in_user

Revision ID: 5b12b14f1b17
Revises: 054cf1ad5052
Create Date: 2020-04-22 09:02:17.199844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b12b14f1b17"
down_revision = "054cf1ad5052"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("hasSeenTutorials", sa.Boolean, nullable=True))


def downgrade():
    op.drop_column("user", "hasSeenTutorials")
