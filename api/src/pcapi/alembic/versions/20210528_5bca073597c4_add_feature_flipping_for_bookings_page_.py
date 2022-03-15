"""add_feature_flipping_for_bookings_page_pre-filters

Revision ID: 5bca073597c4
Revises: 77d29ab6c382
Create Date: 2021-05-28 12:34:10.591044

"""
import enum

from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "5bca073597c4"
down_revision = "77d29ab6c382"
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    ENABLE_BOOKINGS_PAGE_FILTERS_FIRST = "Active le pré-filtrage de la page des réservations"


FLAG = FeatureToggle.ENABLE_BOOKINGS_PAGE_FILTERS_FIRST


def upgrade():
    feature.legacy_add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
