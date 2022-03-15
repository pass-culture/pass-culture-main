"""Add BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS feature flag

Revision ID: 29c8b67b67a5
Revises: d8b409a3cf0c
Create Date: 2021-06-30 11:38:09.161751

"""
from pcapi.models import feature


# revision identifiers, used by Alembic.
revision = "29c8b67b67a5"
down_revision = "d8b409a3cf0c"
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS


def upgrade() -> None:
    feature.legacy_add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
