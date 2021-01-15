"""create_idcheck_feature_flag

Revision ID: 6846a3873abb
Revises: 65e097fd4c74
Create Date: 2021-01-15 10:51:29.909235

"""
from alembic import op

# revision identifiers, used by Alembic.
from pcapi.models.feature import FeatureToggle


revision = "6846a3873abb"
down_revision = "65e097fd4c74"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        f"INSERT INTO feature (name, description, \"isActive\") VALUES ('{FeatureToggle.ALLOW_IDCHECK_REGISTRATION.name}', '{FeatureToggle.ALLOW_IDCHECK_REGISTRATION.value}', True) ON CONFLICT DO NOTHING"
    )


def downgrade():
    op.execute(f"DELETE FROM feature WHERE name = '{FeatureToggle.ALLOW_IDCHECK_REGISTRATION.name}'")
