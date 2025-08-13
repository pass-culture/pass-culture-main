"""
Add UserProfileRefreshCampaign table
Used to store the date after which the user will be asked to update his profile information
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6488ec58e584"
down_revision = "6418ef94834a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_profile_refresh_campaign",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("campaignDate", sa.DateTime(), nullable=False),
        sa.Column("creationDate", sa.DateTime(), nullable=False),
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("updateDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_profile_refresh_campaign", if_exists=True)
