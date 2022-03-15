"""remove_feature_flipping_for_bookings_prefilters

Revision ID: 1ee2283828e7
Revises: f151ee109bd4
Create Date: 2021-07-12 15:35:34.789724

"""
import enum

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "1ee2283828e7"
down_revision = "f151ee109bd4"
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    ENABLE_BOOKINGS_PAGE_FILTERS_FIRST = "Active le pré-filtrage de la page des réservations"


FLAG = FeatureToggle.ENABLE_BOOKINGS_PAGE_FILTERS_FIRST


def upgrade():
    feature.remove_feature_from_database(FLAG)


def downgrade():
    feature.legacy_add_feature_to_database(FLAG)
