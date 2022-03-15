"""Add ENABLE_NEW_VENUE_PAGES feature flag

Revision ID: 8bdc4df58856
Revises: ae87394773a0
Create Date: 2021-05-19 14:06:01.457723

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "8bdc4df58856"
down_revision = "ae87394773a0"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_NEW_VENUE_PAGES


def upgrade():
    feature.legacy_add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
