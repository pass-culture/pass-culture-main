"""feature_enable_venue_withdrawal_details

Revision ID: a249e90c9677
Revises: d8b409a3cf0c
Create Date: 2021-06-30 12:59:01.298321

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "a249e90c9677"
down_revision = "29c8b67b67a5"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.ENABLE_VENUE_WITHDRAWAL_DETAILS


def upgrade():
    feature.add_feature_to_database(FLAG)


def downgrade():
    feature.remove_feature_from_database(FLAG)
