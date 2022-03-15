"""enable phone validation feature

Revision ID: 40754eda1d0f
Revises: 926c8df53762
Create Date: 2021-04-21 07:34:25.619768

"""

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "40754eda1d0f"
down_revision = "926c8df53762"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_PHONE_VALIDATION


def upgrade() -> None:
    feature.legacy_add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
