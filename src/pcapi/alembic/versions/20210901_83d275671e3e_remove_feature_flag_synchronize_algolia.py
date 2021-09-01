"""Remove SYNCHRONIZE_ALGOLIA feature flag"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "83d275671e3e"
down_revision = "0261c634e632"
branch_labels = None
depends_on = None


class DummyFeatureToggle:
    name = "SYNCHRONIZE_ALGOLIA"


def upgrade():
    feature.remove_feature_from_database(DummyFeatureToggle())


def downgrade():
    # No need to add the flag back, it was already unused in the
    # previous version of the backend.
    pass
