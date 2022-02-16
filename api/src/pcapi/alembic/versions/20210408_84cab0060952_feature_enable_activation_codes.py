"""Add ENABLE_ACTIVATION_CODES feature flag"""

# This migration is now a no-op, since the ENABLE_ACTIVATION_CODES
# feature flag has been removed.

# revision identifiers, used by Alembic.
revision = "84cab0060952"
down_revision = "5e52ca521f36"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
