"""Add ENABLE_ACTIVATION_CODES feature flag

Revision ID: 84cab0060952
Revises: 5e52ca521f36
Create Date: 2021-04-08 09:12:50.617498

"""

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "84cab0060952"
down_revision = "5e52ca521f36"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_ACTIVATION_CODES


def upgrade():
    feature.add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
