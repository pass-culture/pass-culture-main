"""feature_enable_isbn_required_in_livre_edition_offer_creation

Revision ID: e5cda043c0ee
Revises: 25468af34cb8
Create Date: 2021-06-07 13:13:20.823519

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "e5cda043c0ee"
down_revision = "25468af34cb8"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION


def upgrade():
    feature.legacy_add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
