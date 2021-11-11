"""Add USE_APP_SEARCH_ON_NATIVE_APP and USE_APP_SEARCH_ON_WEBAPP
feature flags.
"""

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "aaad66e34f30"
down_revision = "0affae55cf74"
branch_labels = None
depends_on = None

FLAGS = (
    feature.FeatureToggle.USE_APP_SEARCH_ON_NATIVE_APP,
    feature.FeatureToggle.USE_APP_SEARCH_ON_WEBAPP,
)


def upgrade() -> None:
    for flag in FLAGS:
        feature.add_feature_to_database(flag)


def downgrade() -> None:
    for flag in FLAGS:
        feature.remove_feature_from_database(flag)
