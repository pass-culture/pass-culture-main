"""
add reason in enum CollectiveBookingCancellationReasons
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "01a23d1b5687"
down_revision = "404b3075d1a4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_EVENT_CANCELLED' ")
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_OVERBOOKING' ")
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_BENEFICIARY_REQUEST' ")
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_OFFER_MODIFIED' ")
    op.execute(
        "ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'BACKOFFICE_OFFER_WITH_WRONG_INFORMATION' "
    )
    op.execute("ALTER TYPE \"bookingcancellationreasons\" ADD VALUE IF NOT EXISTS 'OFFERER_CONNECT_AS' ")


def downgrade() -> None:
    pass
