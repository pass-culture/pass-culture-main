"""Add new feature: AUTO_ACTIVATE_DIGITAL_BOOKINGS

Revision ID: 5e52ca521f36
Revises: 202ae94f2c8f
Create Date: 2021-04-02 15:02:21.218910

"""

from alembic import op
from sqlalchemy.sql import text

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "5e52ca521f36"
down_revision = "202ae94f2c8f"
branch_labels = None
depends_on = None


FEATURE = feature.FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS


def upgrade():
    statement = text(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES (:name, :description, :initial_value)
        """
    )
    statement = statement.bindparams(
        name=FEATURE.name,
        description=FEATURE.value,
        initial_value=FEATURE not in feature.FEATURES_DISABLED_BY_DEFAULT,
    )
    op.execute(statement)


def downgrade():
    statement = text("DELETE FROM feature WHERE name = :name").bindparams(name=FEATURE.name)
    op.execute(statement)
