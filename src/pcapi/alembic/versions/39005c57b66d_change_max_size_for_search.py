"""Change max size for search in recommendation table

Revision ID: 39005c57b66d
Revises: 500ce8194cff
Create Date: 2018-12-19 09:08:06.080825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39005c57b66d'
down_revision = '24f901d09066'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('recommendation', 'search',
        existing_type=sa.VARCHAR(length=300),
        type_=sa.Text,
        existing_nullable=True)


def downgrade():
    op.alter_column('recommendation', 'search',
        existing_type=sa.Text,
        type_=sa.VARCHAR(length=300), existing_nullable=True)
