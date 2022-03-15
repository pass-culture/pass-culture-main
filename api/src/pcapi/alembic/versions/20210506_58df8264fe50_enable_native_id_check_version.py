"""Enable native id check version

Revision ID: 58df8264fe50
Revises: c2e2425fbac6
Create Date: 2021-05-06 15:14:21.619714

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "58df8264fe50"
down_revision = "c2e2425fbac6"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERSION


def upgrade():
    feature.legacy_add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
