"""add_feature_flag_synchronize_venue_provider_in_worker

Revision ID: 877b67c234f9
Revises: 7c8fc9aed6e7
Create Date: 2021-02-15 10:46:05.320883

"""
from alembic import op

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "877b67c234f9"
down_revision = "7c8fc9aed6e7"
branch_labels = None
depends_on = None


def upgrade():
    feature = FeatureToggle.SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER
    op.execute(
        f"""INSERT INTO feature (name, description, "isActive")
        VALUES ('{feature.name}', '{feature.value}', False)
        """
    )


def downgrade():
    feature = FeatureToggle.SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER
    op.execute(f"DELETE FROM feature WHERE name = '{feature.name}'")
