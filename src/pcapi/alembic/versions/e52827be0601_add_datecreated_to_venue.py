"""add_dateCreated_to_venue

Revision ID: e52827be0601
Revises: 678aeab7789e
Create Date: 2020-07-23 15:15:39.384256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e52827be0601'
down_revision = '678aeab7789e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('venue', sa.Column('dateCreated', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('venue', 'dateCreated')
