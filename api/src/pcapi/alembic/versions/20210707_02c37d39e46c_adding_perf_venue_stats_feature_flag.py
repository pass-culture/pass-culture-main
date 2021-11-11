"""Adding PERF_VENUE_STATS feature flag

Revision ID: 02c37d39e46c
Revises: 2f8574b8f1f0
Create Date: 2021-07-07 09:52:21.949266

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "02c37d39e46c"
down_revision = "2f8574b8f1f0"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.PERF_VENUE_STATS


def upgrade() -> None:
    feature.add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
