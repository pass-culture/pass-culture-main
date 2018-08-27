"""Add url to things

Revision ID: 9f958c5e2435
Revises: 72f3629849f0
Create Date: 2018-08-10 14:33:11.028737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f958c5e2435'
down_revision = '6d93c35d097b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('thing', sa.Column('url', sa.VARCHAR(255), nullable=True))


def downgrade():
    pass
