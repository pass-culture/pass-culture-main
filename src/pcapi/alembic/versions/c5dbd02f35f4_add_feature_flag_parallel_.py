"""add_feature_flag_parallel_synchronization_of_venue_provider

Revision ID: c5dbd02f35f4
Revises: 6e99e0e5834d
Create Date: 2021-02-05 17:20:05.483125

"""
from alembic import op

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "c5dbd02f35f4"
down_revision = "6e99e0e5834d"
branch_labels = None
depends_on = None


def upgrade():
    feature = FeatureToggle.PARALLEL_SYNCHRONIZATION_OF_VENUE_PROVIDER
    op.execute(
        f"""INSERT INTO feature (name, description, "isActive")
        VALUES ('{feature.name}', '{feature.value}', False)
        """
    )


def downgrade():
    feature = FeatureToggle.PARALLEL_SYNCHRONIZATION_OF_VENUE_PROVIDER
    op.execute(f"DELETE FROM feature WHERE name = '{feature.name}'")
