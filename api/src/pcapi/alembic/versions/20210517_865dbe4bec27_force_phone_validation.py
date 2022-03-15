"""add_feature_flag

Revision ID: 865dbe4bec27
Revises: 0fe847be8089
Create Date: 2021-05-17 11:04:15.703985

"""

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "865dbe4bec27"
down_revision = "0fe847be8089"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.FORCE_PHONE_VALIDATION


def upgrade() -> None:
    feature.legacy_add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
