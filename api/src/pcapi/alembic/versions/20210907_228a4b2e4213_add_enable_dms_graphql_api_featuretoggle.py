"""add ENABLE_DMS_GRAPHQL_API FeatureToggle
"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "228a4b2e4213"
down_revision = "b15889430729"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.ENABLE_DMS_GRAPHQL_API


def upgrade() -> None:
    feature.add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
