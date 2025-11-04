"""Add `userProfileRefreshCampaign` field to `ActionHistory` model"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cf83b540d8b8"
down_revision = "1ed8548280cd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("action_history", sa.Column("userProfileRefreshCampaignId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "action_history_userProfileRefreshCampaign_fkey",
        "action_history",
        "user_profile_refresh_campaign",
        ["userProfileRefreshCampaignId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("action_history_userProfileRefreshCampaign_fkey", "action_history", type_="foreignkey")
    op.drop_column("action_history", "userProfileRefreshCampaignId")
