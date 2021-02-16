"""add feature flag enable native app recaptcha


Revision ID: 04e6c3b7fd17
Revises: 877b67c234f9
Create Date: 2021-02-16 17:16:00.237475

"""
from alembic import op
from sqlalchemy import text

from pcapi.models.feature import FeatureToggle


# revision identifiers, used by Alembic.
revision = "04e6c3b7fd17"
down_revision = "877b67c234f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    feature = FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA
    op.execute(
        text("""INSERT INTO feature (name, description, "isActive") VALUES (:name, :value, true)""").bindparams(
            name=feature.name, value=feature.value
        )
    )


def downgrade() -> None:
    feature = FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA
    op.execute(text("""DELETE FROM feature WHERE name = :name""").bindparams(name=feature.name))
