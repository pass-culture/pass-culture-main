"""add_feature_flag_offer_validation_computation

Revision ID: bd142e43ea07
Revises: 069e6621725a
Create Date: 2021-03-22 12:07:13.888217

"""
from alembic import op
from sqlalchemy import text

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "bd142e43ea07"
down_revision = "069e6621725a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    feature = FeatureToggle.OFFER_VALIDATION_MOCK_COMPUTATION
    op.execute(
        text("""INSERT INTO feature (name, description, "isActive") VALUES (:name, :value, true)""").bindparams(
            name=feature.name, value=feature.value
        )
    )


def downgrade() -> None:
    feature = FeatureToggle.OFFER_VALIDATION_MOCK_COMPUTATION
    op.execute(text("""DELETE FROM feature WHERE name = :name""").bindparams(name=feature.name))
