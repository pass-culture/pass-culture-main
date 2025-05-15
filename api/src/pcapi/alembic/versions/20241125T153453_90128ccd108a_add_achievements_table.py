"""Add achievements table"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.achievements.models import AchievementEnum
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "90128ccd108a"
down_revision = "0fcad96c98ba"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "achievement",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("bookingId", sa.BigInteger(), nullable=False),
        sa.Column("name", MagicEnum(AchievementEnum), nullable=False),
        sa.Column("unlockedDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("seenDate", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "name", name="user_achievement_unique"),
    )


def downgrade() -> None:
    op.drop_table("achievement")
