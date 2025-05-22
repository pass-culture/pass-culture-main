"""Add new fraud themed reasons to CollectiveBookingCancellationReasons and BookingCancellationReasons"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c3ae9b34287c"
down_revision = "773033aff12a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'FRAUD_SUSPICION' ")
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'FRAUD_INAPPROPRIATE' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'FRAUD_SUSPICION' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'FRAUD_INAPPROPRIATE' ")


def downgrade() -> None:
    pass
