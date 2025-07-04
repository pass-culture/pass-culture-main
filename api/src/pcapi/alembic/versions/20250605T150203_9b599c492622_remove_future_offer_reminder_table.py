"""Drop `future_offer_reminder` table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9b599c492622"
down_revision = "82eb31c662f0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def future_offer_exists() -> bool:
    connection = op.get_bind()
    res = connection.execute("SELECT to_regclass('future_offer')").all()[0][0]
    return res is not None


def upgrade() -> None:
    op.drop_table("future_offer_reminder")


def downgrade() -> None:
    if future_offer_exists():
        op.create_table(
            "future_offer_reminder",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("userId", sa.BigInteger(), nullable=False),
            sa.Column("futureOfferId", sa.BigInteger(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["userId"], ["user.id"], name="future_offer_reminder_userId_fkey", ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["futureOfferId"],
                ["future_offer.id"],
                name="future_offer_reminder_futureOfferId_fkey",
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint("userId", "futureOfferId", name="unique_reminder_per_user_per_future_offer"),
        )
    else:
        op.create_table(
            "future_offer_reminder",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("userId", sa.BigInteger(), nullable=False),
            sa.Column("futureOfferId", sa.BigInteger(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["userId"], ["user.id"], name="future_offer_reminder_userId_fkey", ondelete="CASCADE"
            ),
            sa.UniqueConstraint("userId", "futureOfferId", name="unique_reminder_per_user_per_future_offer"),
        )
