"""Add new OFFERER_CLOSED reason in BookingCancellationReasons and CollectiveBookingCancellationReasons"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e9c8d83f71ce"
down_revision = "feb74e81bf45"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'OFFERER_CLOSED' ")
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'OFFERER_CLOSED' ")


def downgrade() -> None:
    pass
