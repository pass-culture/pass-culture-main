"""This migration added the PERF_VENUE_STATS feature flag, but it's
now a no-op because this feature flag has been removed.

Revision ID: 02c37d39e46c
Revises: 2f8574b8f1f0
Create Date: 2021-07-07 09:52:21.949266

"""

# revision identifiers, used by Alembic.
revision = "02c37d39e46c"
down_revision = "2f8574b8f1f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
