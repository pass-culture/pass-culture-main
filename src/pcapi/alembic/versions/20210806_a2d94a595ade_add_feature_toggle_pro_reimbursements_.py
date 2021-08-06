"""add_feature_toggle_pro_reimbursements_filters

Revision ID: a2d94a595ade
Revises: c016332e7bfb
Create Date: 2021-08-06 14:40:47.241921

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "a2d94a595ade"
down_revision = "c016332e7bfb"
branch_labels = None
depends_on = None

FLAG = feature.FeatureToggle.PRO_REIMBURSEMENTS_FILTERS


def upgrade() -> None:
    feature.add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
