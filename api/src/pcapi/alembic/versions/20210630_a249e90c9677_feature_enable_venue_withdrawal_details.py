"""feature_enable_venue_withdrawal_details

This migration is now a no-op, since the ENABLE_VENUE_WITHDRAWAL_DETAILS
feature flag is not defined anymore.
"""


# revision identifiers, used by Alembic.
revision = "a249e90c9677"
down_revision = "29c8b67b67a5"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
