"""remove_feature_disable_booking_recap

Revision ID: 7fb77ba30cde
Revises: 289494f36088
Create Date: 2021-08-26 15:06:53.087556

"""
import enum

# revision identifiers, used by Alembic.
from pcapi.models import feature


revision = "7fb77ba30cde"
down_revision = "289494f36088"
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    DISABLE_BOOKINGS_RECAP_FOR_SOME_PROS = (
        "Désactivation de l'appel qui est fait sur la route mes réservations pour certains acteurs"
    )


FLAG = FeatureToggle.DISABLE_BOOKINGS_RECAP_FOR_SOME_PROS


def upgrade():
    feature.remove_feature_from_database(FLAG)


def downgrade():
    feature.add_feature_to_database(FLAG)
