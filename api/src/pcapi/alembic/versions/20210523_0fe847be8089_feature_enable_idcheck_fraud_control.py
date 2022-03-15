"""feature enable idcheck fraud control

Revision ID: 0fe847be8089
Revises: 6999a11484ba
Create Date: 2021-05-23 15:49:25.049504

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "0fe847be8089"
down_revision = "6999a11484ba"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS


def upgrade() -> None:
    feature.legacy_add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
