"""add_feature_toggle_eac_indiv

This migration is now a no-op, since the ENABLE_NATIVE_EAC_INDIVIDUAL
feature flag is not defined anymore.

Revision ID: e65789e45741
Revises: 5d94e6b5f8f3
Create Date: 2021-08-26 10:05:59.627682

"""

# revision identifiers, used by Alembic.
revision = "e65789e45741"
down_revision = "5d94e6b5f8f3"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
