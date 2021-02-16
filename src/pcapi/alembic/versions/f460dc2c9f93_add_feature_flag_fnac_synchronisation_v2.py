"""add_feature_flag_fnac_synchronisation_v2

Revision ID: f460dc2c9f93
Revises: 04e6c3b7fd17
Create Date: 2021-02-16 15:23:13.378617

"""
from alembic import op
from sqlalchemy import text

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "f460dc2c9f93"
down_revision = "04e6c3b7fd17"
branch_labels = None
depends_on = None


def upgrade() -> None:
    feature = FeatureToggle.FNAC_SYNCHRONIZATION_V2
    op.execute(
        text("""INSERT INTO feature (name, description, "isActive") VALUES (:name, :value, true)""").bindparams(
            name=feature.name, value=feature.value
        )
    )


def downgrade() -> None:
    feature = FeatureToggle.FNAC_SYNCHRONIZATION_V2
    op.execute(text("""DELETE FROM feature WHERE name = :name""").bindparams(name=feature.name))
