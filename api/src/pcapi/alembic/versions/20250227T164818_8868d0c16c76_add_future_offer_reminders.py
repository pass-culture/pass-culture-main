"""Add future offers reminders"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8868d0c16c76"
down_revision = "50fe0db503c3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "future_offer_reminder",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("futureOfferId", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "futureOfferId", name="unique_reminder_per_user_per_future_offer"),
        if_not_exists=True
    )


def downgrade() -> None:
    op.drop_table("future_offer_reminder", if_exists=True)
