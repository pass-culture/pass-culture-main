"""Add future offers reminders

add_future_offer_reminders
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "060ef534e1a5"
down_revision = "1ec374800b10"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "future_offer_reminder",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("offer_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offer.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_future_offer_reminder_offer_id"), "future_offer_reminder", ["offer_id"], unique=False)
    op.create_index(op.f("ix_future_offer_reminder_user_id"), "future_offer_reminder", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("future_offer_reminder")
