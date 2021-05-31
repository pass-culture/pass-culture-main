"""Add ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING feature flag

Revision ID: 8bdc4dd58856
Revises: 5bca073597c4
Create Date: 2021-05-31 09:54:01.457723

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "8bdc4dd58856"
down_revision = "5bca073597c4"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING


def upgrade():
    feature.add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
