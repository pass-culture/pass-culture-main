"""add_pro_homepage_feature_flipping

Revision ID: a5e003094c15
Revises: 9a2cd2388d90
Create Date: 2021-01-29 14:54:31.343722

"""
from alembic import op

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "a5e003094c15"
down_revision = "9a2cd2388d90"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        f"INSERT INTO feature (name, description, \"isActive\") VALUES ('{FeatureToggle.PRO_HOMEPAGE.name}', '{FeatureToggle.PRO_HOMEPAGE.value}', False)"
    )


def downgrade():
    op.execute(f"DELETE FROM feature WHERE name = '{FeatureToggle.PRO_HOMEPAGE.name}'")
