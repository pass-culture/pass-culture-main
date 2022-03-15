"""Add feature flag ID_CHECK_ADDRESS_AUTOCOMPLETION

Revision ID: 84706f806e3d
Revises: aaad66e34f30
Create Date: 2021-06-17 12:38:31.584852

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "84706f806e3d"
down_revision = "aaad66e34f30"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION


def upgrade():
    feature.legacy_add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
