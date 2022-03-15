"""Add ENABLE_ID_CHECK_RETENTION feature flag

Revision ID: e85a73abc5a7
Revises: a3a703bc054b
Create Date: 2021-06-04 08:00:13.749757

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "e85a73abc5a7"
down_revision = "a3a703bc054b"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.ENABLE_ID_CHECK_RETENTION


def upgrade():
    feature.legacy_add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
