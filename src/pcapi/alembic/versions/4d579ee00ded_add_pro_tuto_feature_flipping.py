"""add_pro_tuto_feature_flipping

Revision ID: 4d579ee00ded
Revises: a5e003094c15
Create Date: 2021-01-29 15:57:05.834565

"""
from alembic import op

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "4d579ee00ded"
down_revision = "a5e003094c15"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        f"INSERT INTO feature (name, description, \"isActive\") VALUES ('{FeatureToggle.PRO_TUTO.name}', '{FeatureToggle.PRO_TUTO.value}', False)"
    )


def downgrade():
    op.execute(f"DELETE FROM feature WHERE name = '{FeatureToggle.PRO_TUTO.name}'")
