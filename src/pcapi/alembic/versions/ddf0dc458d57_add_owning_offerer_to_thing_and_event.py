"""add owning_offerer_id to event and thing

Revision ID: ddf0dc458d57
Revises: 5eeaa2f48327
Create Date: 2019-03-18 16:20:16.770962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddf0dc458d57'
down_revision = '5eeaa2f48327'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('thing', sa.Column('owningOffererId', sa.Integer, nullable=True))
    op.add_column('event', sa.Column('owningOffererId', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('thing', 'owningOffererId')
    op.drop_column('event', 'owningOffererId')
