"""
add_reason_in_enum_BookingCancellationReasons
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fdc8ef1d0791"
down_revision = "c60f1f384721"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_EVENT_CANCELLED' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_SURBOOKING' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_BENEFICIARY_REQUEST' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_OFFER_MODIFIED' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_OFFER_ERROR' ")
    op.execute("ALTER TYPE \"cancellation_reason\" ADD VALUE IF NOT EXISTS 'OFFERER_CONNECT_AS' ")


def downgrade() -> None:
    pass
