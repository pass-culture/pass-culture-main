"""add_feature_flag_enable_whole_venue_provider_algolia_indexation

Revision ID: 85adf538245f
Revises: c5dbd02f35f4
Create Date: 2021-02-05 17:41:56.500901

"""
from alembic import op

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "85adf538245f"
down_revision = "c5dbd02f35f4"
branch_labels = None
depends_on = None


def upgrade():
    feature = FeatureToggle.ENABLE_WHOLE_VENUE_PROVIDER_ALGOLIA_INDEXATION
    op.execute(
        f"""INSERT INTO feature (name, description, "isActive")
        VALUES ('{feature.name}', '{feature.value}', False)
        """
    )


def downgrade():
    feature = FeatureToggle.ENABLE_WHOLE_VENUE_PROVIDER_ALGOLIA_INDEXATION
    op.execute(f"DELETE FROM feature WHERE name = '{feature.name}'")
