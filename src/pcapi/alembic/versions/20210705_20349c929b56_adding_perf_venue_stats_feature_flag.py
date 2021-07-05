"""Adding PERF_VENUE_STATS feature flag

Revision ID: 20349c929b56
Revises: d9f2a9027e7d
Create Date: 2021-07-05 14:06:52.076002

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "20349c929b56"
down_revision = "d9f2a9027e7d"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.PERF_VENUE_STATS


def upgrade() -> None:
    feature.add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
