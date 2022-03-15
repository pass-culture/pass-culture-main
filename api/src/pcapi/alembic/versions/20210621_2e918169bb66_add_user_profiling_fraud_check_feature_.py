"""Add USER_PROFILING_FRAUD_CHECK feature flag

Revision ID: 2e918169bb66
Revises: 84706f806e3d
Create Date: 2021-06-21 07:39:28.931418

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "2e918169bb66"
down_revision = "84706f806e3d"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.USER_PROFILING_FRAUD_CHECK


def upgrade() -> None:
    feature.legacy_add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
