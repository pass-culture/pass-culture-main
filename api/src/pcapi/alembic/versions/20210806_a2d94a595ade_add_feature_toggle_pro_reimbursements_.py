"""add_feature_toggle_pro_reimbursements_filters

This migration is now a no-op, since the PRO_REIMBURSEMENTS_FILTERS
feature flag is not defined anymore.
"""


# revision identifiers, used by Alembic.
revision = "a2d94a595ade"
down_revision = "c016332e7bfb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
