"""Add WEBAPP_V2_ENABLED feature flag

Revision ID: bebba9216847
Revises: ff887e7b4f89
Create Date: 2021-08-03 17:27:45.546319

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "bebba9216847"
down_revision = "ff887e7b4f89"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.WEBAPP_V2_ENABLED


def upgrade() -> None:
    feature.add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
