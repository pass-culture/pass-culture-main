"""create index ix_action_history_userProfileRefreshCampaignId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fd9866e3fe0c"
down_revision = "75e6a6f826e6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.create_index(
        "ix_action_history_userProfileRefreshCampaignId",
        "action_history",
        ["userProfileRefreshCampaignId"],
        unique=False,
        postgresql_where=sa.text('"userProfileRefreshCampaignId" IS NOT NULL'),
        if_not_exists=True,
        postgresql_concurrently=True,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        "ix_action_history_userProfileRefreshCampaignId",
        table_name="action_history",
        postgresql_where=sa.text('"userProfileRefreshCampaignId" IS NOT NULL'),
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.execute("BEGIN")
