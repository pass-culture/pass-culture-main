"""add_venue_provider_sync_container_id

Revision ID: 5a092d53ee0a
Revises: 6b76c225cc26
Create Date: 2019-12-10 10:39:52.358799

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5a092d53ee0a'
down_revision = '6b76c225cc26'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('venue_provider', sa.Column('syncWorkerId', sa.VARCHAR(24), nullable=True))


def downgrade():
    op.drop_column('venue_provider', 'syncWorkerId')
