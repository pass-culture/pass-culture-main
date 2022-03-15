"""add feature flag DISPLAY_DMS_REDIRECTION

Revision ID: 963e6e163cf0
Revises: 2c062a40154e
Create Date: 2021-05-25 16:56:31.360153

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "963e6e163cf0"
down_revision = "2c062a40154e"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.DISPLAY_DMS_REDIRECTION


def upgrade() -> None:
    feature.legacy_add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
