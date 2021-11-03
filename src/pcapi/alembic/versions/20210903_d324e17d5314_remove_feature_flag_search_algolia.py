"""Remove SEARCH_ALGOLIA feature flag"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "d324e17d5314"
down_revision = "83d275671e3e"
branch_labels = None
depends_on = None


class DummyFeatureToggle:
    name = "SEARCH_ALGOLIA"


def upgrade():
    feature.remove_feature_from_database(DummyFeatureToggle())


def downgrade():
    # No need to add the flag back, it was already unused in the
    # previous version of the backend.
    pass
