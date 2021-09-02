"""add_feature_toggle_new_auto_expiry_bookings

Revision ID: 51ac2a874ba9
Revises: 83d275671e3e
Create Date: 2021-09-06 08:50:18.791419

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "51ac2a874ba9"
down_revision = "83d275671e3e"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS


def upgrade():
    feature.add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
