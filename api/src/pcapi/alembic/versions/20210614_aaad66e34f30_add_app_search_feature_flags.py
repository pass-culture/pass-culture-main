"""Add USE_APP_SEARCH_ON_NATIVE_APP and USE_APP_SEARCH_ON_WEBAPP
feature flags.

This migration is now a no-op, since these features are not defined
anymore.
"""


# revision identifiers, used by Alembic.
revision = "aaad66e34f30"
down_revision = "0affae55cf74"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
