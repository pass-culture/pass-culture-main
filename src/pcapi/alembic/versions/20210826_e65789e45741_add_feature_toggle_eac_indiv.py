"""add_feature_toggle_eac_indiv

Revision ID: e65789e45741
Revises: 5d94e6b5f8f3
Create Date: 2021-08-26 10:05:59.627682

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "e65789e45741"
down_revision = "5d94e6b5f8f3"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL


def upgrade():
    feature.add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
