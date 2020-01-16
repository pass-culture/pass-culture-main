"""Drop column thingId on Offer

Revision ID: f98d8cea0564
Revises: 99339c9d58b1
Create Date: 2019-05-21 09:22:42.053229

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f98d8cea0564'
down_revision = '99339c9d58b1'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('offer', 'thingId')


def downgrade():
    op.add_column('offer', sa.Column('thingId', sa.BigInteger, index=True, nullable=True))
