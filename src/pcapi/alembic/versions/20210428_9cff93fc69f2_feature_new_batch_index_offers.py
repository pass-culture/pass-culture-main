"""Add new feature flag: USE_NEW_BATCH_INDEX_OFFERS_BEHAVIOUR

Revision ID: 9cff93fc69f2
Revises: ff04dc8fe18e
Create Date: 2021-04-28 17:44:43.120881
"""

# This migration added the USE_NEW_BATCH_INDEX_OFFERS_BEHAVIOUR
# feature flag. But this flag has been removed in a later
# migration. Keep this as a no-op until we squash this migration, so
# that all migration files can be loaded by Alembic and played on an
# empty database.


# revision identifiers, used by Alembic.
revision = "9cff93fc69f2"
down_revision = "ff04dc8fe18e"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
