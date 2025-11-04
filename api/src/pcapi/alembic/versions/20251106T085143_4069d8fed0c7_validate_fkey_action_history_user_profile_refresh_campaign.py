"""Validate constraint action_history_userProfileRefreshCampaign_fkey"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4069d8fed0c7"
down_revision = "864fbd2feb03"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE action_history VALIDATE CONSTRAINT "action_history_userProfileRefreshCampaign_fkey" """)
    op.execute("""ALTER TABLE action_history VALIDATE CONSTRAINT "check_action_resource" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
