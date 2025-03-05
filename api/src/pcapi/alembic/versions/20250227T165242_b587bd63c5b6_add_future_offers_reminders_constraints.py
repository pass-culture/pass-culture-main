"""Add FutureOffer Reminders constraints"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b587bd63c5b6"
down_revision = "6de6b0acf802"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "future_offer_reminder_userId_fkey",
        "future_offer_reminder",
        "user",
        ["userId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "future_offer_reminder_futureOfferId_fkey",
        "future_offer_reminder",
        "future_offer",
        ["futureOfferId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("future_offer_reminder_userId_fkey", "future_offer_reminder", type_="foreignkey")
    op.drop_constraint("future_offer_reminder_futureOfferId_fkey", "future_offer_reminder", type_="foreignkey")
