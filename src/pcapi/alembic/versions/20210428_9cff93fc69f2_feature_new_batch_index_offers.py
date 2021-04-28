"""Add new feature flag: USE_NEW_BATCH_INDEX_OFFERS_BEHAVIOUR

Revision ID: 9cff93fc69f2
Revises: ff04dc8fe18e
Create Date: 2021-04-28 17:44:43.120881
"""

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "9cff93fc69f2"
down_revision = "ff04dc8fe18e"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.USE_NEW_BATCH_INDEX_OFFERS_BEHAVIOUR


def upgrade():
    feature.add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
